"""
Revvy AI Companion - API Server
Provides a REST API for the frontend and mobile app to interact with Revvy.
"""

import os
import time
import logging
import threading
import json
import traceback
from datetime import datetime
import asyncio
import websockets
from aiohttp import web
import aiohttp_cors

logger = logging.getLogger("APIServer")

class APIServer:
    """API Server for Revvy AI Companion"""
    
    def __init__(self, config, revvy_core):
        self.config = config
        self.revvy_core = revvy_core
        self.running = False
        self.thread = None
        self.app = None
        self.runner = None
        self.site = None
        self.websocket_server = None
        self.websocket_clients = set()
        
        # API settings
        self.host = self.config.API_HOST
        self.port = self.config.API_PORT
    
    def start(self):
        """Start API server"""
        self.running = True
        self.thread = threading.Thread(target=self._start_server)
        self.thread.daemon = True
        self.thread.start()
        logger.info(f"API Server starting on {self.host}:{self.port}")
    
    def stop(self):
        """Stop API server"""
        self.running = False
        if self.runner:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._shutdown())
            loop.close()
        logger.info("API Server stopped")
    
    async def _shutdown(self):
        """Shutdown API server"""
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()
        
        # Close all websocket connections
        if self.websocket_clients:
            for ws in self.websocket_clients:
                try:
                    await ws.close()
                except:
                    pass
    
    def _start_server(self):
        """Start API server in a separate thread"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Create AIOHTTP web app
        self.app = web.Application()
        
        # Setup routes
        self._setup_routes()
        
        # Setup CORS
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*"
            )
        })
        
        # Apply CORS to all routes
        for route in list(self.app.router.routes()):
            cors.add(route)
        
        # Run the server
        self.runner = web.AppRunner(self.app)
        loop.run_until_complete(self.runner.setup())
        self.site = web.TCPSite(self.runner, self.host, self.port)
        loop.run_until_complete(self.site.start())
        
        # Start websocket server
        loop.run_until_complete(self._start_websocket_server())
        
        logger.info(f"API Server running on http://{self.host}:{self.port}")
        
        # Run event loop
        try:
            loop.run_forever()
        except Exception as e:
            logger.error(f"Error in API server event loop: {e}")
            logger.error(traceback.format_exc())
        finally:
            loop.close()
    
    def _setup_routes(self):
        """Setup API routes"""
        self.app.router.add_get('/', self._handle_index)
        self.app.router.add_get('/api/status', self._handle_status)
        self.app.router.add_get('/api/system/status', self._handle_system_status)
        self.app.router.add_post('/api/system/reconnect', self._handle_reconnect_components)
        self.app.router.add_get('/api/vehicle', self._handle_vehicle_data)
        self.app.router.add_get('/api/mode', self._handle_get_mode)
        self.app.router.add_post('/api/mode', self._handle_set_mode)
        self.app.router.add_post('/api/voice/command', self._handle_voice_command)
        self.app.router.add_get('/api/achievements', self._handle_get_achievements)
        self.app.router.add_post('/api/dtc/clear', self._handle_clear_dtc)
        self.app.router.add_get('/api/dtc/explanation/{code}', self._handle_get_dtc_explanation)
        
        # Unit settings routes
        self.app.router.add_get('/api/settings/units', self._handle_get_unit_settings)
        self.app.router.add_post('/api/settings/units/toggle', self._handle_toggle_unit_system)
    
    async def _start_websocket_server(self):
        """Start websocket server for real-time updates"""
        self.websocket_server = await websockets.serve(
            self._handle_websocket,
            self.host,
            self.port + 1  # Use port+1 for websockets
        )
        logger.info(f"WebSocket server running on ws://{self.host}:{self.port+1}")
    
    async def _handle_websocket(self, websocket, path):
        """Handle websocket connections"""
        # Register client
        self.websocket_clients.add(websocket)
        logger.info(f"WebSocket client connected: {websocket.remote_address}")
        
        try:
            # Keep connection alive and handle messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self._process_websocket_message(websocket, data)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from client: {message}")
                except Exception as e:
                    logger.error(f"Error processing client message: {e}")
                    logger.error(traceback.format_exc())
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"WebSocket client disconnected: {websocket.remote_address}")
        finally:
            # Unregister client
            self.websocket_clients.remove(websocket)
    
    async def _process_websocket_message(self, websocket, data):
        """Process websocket message"""
        # Handle different message types
        message_type = data.get('type')
        
        if message_type == 'subscribe':
            # Client subscribing to events
            logger.info(f"Client subscribed to events: {data.get('events', [])}")
            
            # Send initial vehicle data
            await self._send_vehicle_data(websocket)
        
        elif message_type == 'voice_command':
            # Handle voice command
            command = data.get('command')
            if command:
                logger.info(f"Voice command via WebSocket: {command}")
                
                # Process with AI engine
                query_id = self.revvy_core.ai.query(
                    command,
                    callback=lambda qid, response: asyncio.run(
                        self._send_ai_response(websocket, qid, response)
                    )
                )
                
                # Send acknowledgement
                await websocket.send(json.dumps({
                    'type': 'command_received',
                    'query_id': query_id
                }))
    
    async def _send_ai_response(self, websocket, query_id, response):
        """Send AI response to client"""
        try:
            await websocket.send(json.dumps({
                'type': 'ai_response',
                'query_id': query_id,
                'text': response
            }))
            
            # Also speak the response if voice is enabled
            if self.revvy_core.voice.voice_enabled:
                self.revvy_core.voice.speak(response)
                
        except Exception as e:
            logger.error(f"Error sending AI response: {e}")
            logger.error(traceback.format_exc())
    
    async def _send_vehicle_data(self, websocket):
        """Send current vehicle data to client"""
        try:
            if self.revvy_core.obd:
                data = self.revvy_core.obd.get_vehicle_data_with_units()
                await websocket.send(json.dumps({
                    'type': 'vehicle_data',
                    'data': data
                }))
        except Exception as e:
            logger.error(f"Error sending vehicle data: {e}")
            logger.error(traceback.format_exc())
    
    async def _handle_index(self, request):
        """Handle index route"""
        return web.json_response({
            'name': 'Revvy AI Companion API',
            'version': self.config.get('system', 'version'),
            'status': 'online',
            'timestamp': datetime.now().isoformat()
        })
    
    async def _handle_status(self, request):
        """Handle status route"""
        return web.json_response({
            'status': 'online',
            'obd_connected': self.revvy_core.obd.is_connected() if self.revvy_core.obd else False,
            'voice_enabled': self.revvy_core.voice.voice_enabled if self.revvy_core.voice else False,
            'current_mode': self.revvy_core.current_mode,
            'current_personality': self.revvy_core.current_personality,
            'system_ready': self.revvy_core.system_ready,
            'timestamp': datetime.now().isoformat()
        })
    
    async def _handle_system_status(self, request):
        """Handle system status route with component details"""
        if not self.revvy_core:
            return web.json_response({
                'error': 'Core not initialized'
            }, status=500)
        
        status = {
            'status': 'online',
            'obd_connected': self.revvy_core.obd.is_connected() if self.revvy_core.obd else False,
            'gps_active': self.revvy_core.gps.is_active() if self.revvy_core.gps else False,
            'voice_enabled': self.revvy_core.voice.voice_enabled if self.revvy_core.voice else False,
            'ai_available': self.revvy_core.component_status['ai']['available'],
            'current_mode': self.revvy_core.current_mode,
            'current_personality': self.revvy_core.current_personality,
            'system_ready': self.revvy_core.system_ready,
            'components': self.revvy_core.component_status,
            'unit_system': self.revvy_core.config.get('display', 'unit_system'),
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Add system metrics
            import psutil
            status['system_metrics'] = {
                'cpu_usage': psutil.cpu_percent(),
                'memory_usage': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'uptime': time.time() - psutil.boot_time()
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            status['system_metrics'] = {}
        
        return web.json_response(status)

    async def _handle_reconnect_components(self, request):
        """Handle component reconnection route"""
        if not self.revvy_core:
            return web.json_response({
                'error': 'Core not initialized'
            }, status=500)
        
        results = {}
        
        # Try to reconnect OBD
        if self.revvy_core.component_status['obd']['available']:
            try:
                if self.revvy_core.obd:
                    self.revvy_core.obd.restart()
                    results['obd'] = 'Reconnect initiated'
            except Exception as e:
                results['obd'] = f'Error: {str(e)}'
        
        # Try to reconnect GPS
        if self.revvy_core.component_status['gps']['available']:
            try:
                if self.revvy_core.gps:
                    self.revvy_core.gps.restart()
                    results['gps'] = 'Reconnect initiated'
            except Exception as e:
                results['gps'] = f'Error: {str(e)}'
        
        # Try to reconnect voice
        if self.revvy_core.component_status['voice']['available']:
            try:
                if self.revvy_core.voice:
                    self.revvy_core.voice.restart()
                    results['voice'] = 'Reconnect initiated'
            except Exception as e:
                results['voice'] = f'Error: {str(e)}'
        
        return web.json_response({
            'success': True,
            'results': results
        })
    
    async def _handle_vehicle_data(self, request):
        """Handle vehicle data route"""
        if not self.revvy_core.obd:
            return web.json_response({'error': 'OBD not initialized'}, status=500)
        
        unit_system = self.revvy_core.config.get("display", "unit_system")
        
        if unit_system == "imperial":
            data = self.revvy_core.obd.get_vehicle_data_with_units()
        else:
            data = self.revvy_core.obd.get_vehicle_data()
            # Add unit labels for metric
            if "speed" in data:
                data["speed_unit"] = "km/h"
            
            for temp_field in ["coolant_temp", "intake_temp", "oil_temp"]:
                if temp_field in data:
                    data[f"{temp_field}_unit"] = "C"
            
            if "boost_pressure" in data:
                data["boost_pressure_unit"] = "kPa"
                
        return web.json_response(data)
    
    async def _handle_get_mode(self, request):
        """Handle get mode route"""
        return web.json_response({
            'mode': self.revvy_core.current_mode,
            'personality': self.revvy_core.current_personality
        })
    
    async def _handle_set_mode(self, request):
        """Handle set mode route"""
        try:
            data = await request.json()
            mode = data.get('mode')
            
            if not mode:
                return web.json_response({'error': 'Mode is required'}, status=400)
            
            if self.revvy_core.change_mode(mode):
                return web.json_response({
                    'success': True,
                    'mode': self.revvy_core.current_mode,
                    'personality': self.revvy_core.current_personality
                })
            else:
                return web.json_response({'error': 'Invalid mode'}, status=400)
                
        except Exception as e:
            logger.error(f"Error setting mode: {e}")
            logger.error(traceback.format_exc())
            return web.json_response({'error': str(e)}, status=500)
    
    async def _handle_voice_command(self, request):
        """Handle voice command route"""
        try:
            data = await request.json()
            command = data.get('command')
            
            if not command:
                return web.json_response({'error': 'Command is required'}, status=400)
            
            # Process with AI engine
            query_id = self.revvy_core.ai.query(command)
            
            return web.json_response({
                'success': True,
                'query_id': query_id,
                'message': 'Command received'
            })
                
        except Exception as e:
            logger.error(f"Error processing voice command: {e}")
            logger.error(traceback.format_exc())
            return web.json_response({'error': str(e)}, status=500)
    
    async def _handle_get_achievements(self, request):
        """Handle get achievements route"""
        return web.json_response(self.config.ACHIEVEMENTS)
    
    async def _handle_clear_dtc(self, request):
        """Handle clear DTC route"""
        if not self.revvy_core.obd:
            return web.json_response({'error': 'OBD not initialized'}, status=500)
        
        try:
            success = self.revvy_core.obd.clear_dtc_codes()
            
            if success:
                return web.json_response({
                    'success': True,
                    'message': 'DTC codes cleared successfully'
                })
            else:
                return web.json_response({
                    'success': False,
                    'error': 'Failed to clear DTC codes'
                }, status=500)
                
        except Exception as e:
            logger.error(f"Error clearing DTC codes: {e}")
            logger.error(traceback.format_exc())
            return web.json_response({'error': str(e)}, status=500)
    
    async def _handle_get_dtc_explanation(self, request):
        """Handle get DTC explanation route"""
        code = request.match_info.get('code')
        
        if not code:
            return web.json_response({'error': 'DTC code is required'}, status=400)
        
        # Get explanation from AI
        explanation = await self._get_dtc_explanation(code)
        
        return web.json_response(explanation)
    
    async def _handle_get_unit_settings(self, request):
        """Handle get unit settings route"""
        if not self.revvy_core or not self.revvy_core.config:
            return web.json_response({'error': 'Config not initialized'}, status=500)
        
        unit_settings = {
            'unit_system': self.revvy_core.config.get("display", "unit_system"),
            'temperature_unit': self.revvy_core.config.get("display", "temperature_unit"),
            'pressure_unit': self.revvy_core.config.get("display", "pressure_unit"),
            'distance_unit': self.revvy_core.config.get("display", "distance_unit"),
            'speed_unit': self.revvy_core.config.get("display", "speed_unit")
        }
        
        return web.json_response(unit_settings)

    async def _handle_toggle_unit_system(self, request):
        """Handle toggle unit system route"""
        if not self.revvy_core or not self.revvy_core.config:
            return web.json_response({'error': 'Config not initialized'}, status=500)
        
        try:
            data = await request.json()
            unit_system = data.get('unit_system')
            
            if unit_system not in ['metric', 'imperial']:
                return web.json_response({'error': 'Invalid unit system'}, status=400)
            
            # Update unit system
            current_system = self.revvy_core.config.get("display", "unit_system")
            
            if unit_system != current_system:
                # Set unit system
                self.revvy_core.config.set("display", "unit_system", unit_system)
                
                # Update related units based on the system
                if unit_system == 'metric':
                    self.revvy_core.config.set("display", "temperature_unit", "celsius")
                    self.revvy_core.config.set("display", "pressure_unit", "kpa")
                    self.revvy_core.config.set("display", "distance_unit", "km")
                    self.revvy_core.config.set("display", "speed_unit", "kph")
                else:
                    self.revvy_core.config.set("display", "temperature_unit", "fahrenheit")
                    self.revvy_core.config.set("display", "pressure_unit", "psi")
                    self.revvy_core.config.set("display", "distance_unit", "mi")
                    self.revvy_core.config.set("display", "speed_unit", "mph")
                
                # Notify clients of the change
                self.broadcast_event('unit_system_changed', {
                    'unit_system': unit_system
                })
            
            return web.json_response({
                'success': True,
                'unit_system': unit_system
            })
            
        except Exception as e:
            logger.error(f"Error toggling unit system: {e}")
            logger.error(traceback.format_exc())
            return web.json_response({'error': str(e)}, status=500)
    
    async def _get_dtc_explanation(self, code):
        """Get explanation for DTC code"""
        # This is a placeholder - in a real implementation, we would query a database 
        # or use the AI engine to generate an explanation
        
        # Sample explanations for common codes
        explanations = {
            'P0300': {
                'description': 'Random/Multiple Cylinder Misfire Detected',
                'severity': 'High',
                'possibleCauses': [
                    'Faulty spark plugs or wires',
                    'Fuel injector issues',
                    'Low fuel pressure',
                    'Vacuum leaks',
                    'Low compression'
                ],
                'possibleFixes': [
                    'Replace spark plugs and wires',
                    'Clean or replace fuel injectors',
                    'Check fuel pressure',
                    'Inspect for vacuum leaks',
                    'Perform compression test'
                ]
            },
            'P0420': {
                'description': 'Catalyst System Efficiency Below Threshold (Bank 1)',
                'severity': 'Medium',
                'possibleCauses': [
                    'Failing catalytic converter',
                    'Exhaust leaks',
                    'Faulty oxygen sensors',
                    'Engine misfires'
                ],
                'possibleFixes': [
                    'Replace catalytic converter',
                    'Repair exhaust leaks',
                    'Replace oxygen sensors',
                    'Address engine misfire causes'
                ]
            }
        }
        
        # Return explanation if available, otherwise generate a generic one
        if code in explanations:
            return explanations[code]
        else:
            return {
                'description': f'Diagnostic Trouble Code {code}',
                'severity': 'Unknown',
                'possibleCauses': [
                    'Multiple possible causes',
                    'Consult vehicle service manual or mechanic'
                ],
                'possibleFixes': [
                    'Scan for additional codes',
                    'Perform vehicle-specific diagnostics',
                    'Consult a professional mechanic'
                ]
            }
    
    def broadcast_event(self, event_type, data):
        """Broadcast event to all connected websocket clients"""
        if not self.websocket_clients:
            return
        
        message = json.dumps({
            'type': event_type,
            **data
        })
        
        # Schedule broadcast in event loop
        asyncio.run(self._broadcast_message(message))
    
    async def _broadcast_message(self, message):
        """Broadcast message to all websocket clients"""
        if not self.websocket_clients:
            return
        
        disconnected_clients = set()
        
        for client in self.websocket_clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                logger.error(f"Error sending message to client: {e}")
                logger.error(traceback.format_exc())
                disconnected_clients.add(client)
        
        # Remove disconnected clients
        for client in disconnected_clients:
            self.websocket_clients.remove(client)