import json
import hashlib
import random
import datetime
import pytz
from typing import Dict, Any, Optional

class ToolManager:
    """Manages tool definitions and executions for the emotional companion assistant."""
    
    def __init__(self):
        """Initialize the tool manager with available tools."""
        self.tools = {
            "getdateandtimetool": self.get_date_and_time,
            "trackordertool": self.track_order,
            "getweathertool": self.get_weather,
            "getmoodsuggestiontool": self.get_mood_suggestion
        }
    
    def get_tool_definitions(self) -> list:
        """Return the tool definitions for Nova Sonic prompt configuration."""
        get_default_tool_schema = json.dumps({
            "type": "object",
            "properties": {},
            "required": []
        })

        get_order_tracking_schema = json.dumps({
            "type": "object",
            "properties": {
                "orderId": {
                    "type": "string",
                    "description": "The order number or ID to track"
                },
                "requestNotifications": {
                    "type": "boolean",
                    "description": "Whether to set up notifications for this order",
                    "default": False
                }
            },
            "required": ["orderId"]
        })
        
        get_weather_schema = json.dumps({
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city or location to get weather for"
                },
                "unit": {
                    "type": "string",
                    "description": "Temperature unit (celsius or fahrenheit)",
                    "enum": ["celsius", "fahrenheit"],
                    "default": "celsius"
                }
            },
            "required": ["location"]
        })
        
        get_mood_suggestion_schema = json.dumps({
            "type": "object",
            "properties": {
                "currentMood": {
                    "type": "string",
                    "description": "The user's current mood or emotional state"
                },
                "intensity": {
                    "type": "string",
                    "description": "The intensity of the mood (mild, moderate, intense)",
                    "enum": ["mild", "moderate", "intense"],
                    "default": "moderate"
                }
            },
            "required": ["currentMood"]
        })
        
        return [
            {
                "toolSpec": {
                    "name": "getDateAndTimeTool",
                    "description": "Get information about the current date and time",
                    "inputSchema": {
                        "json": get_default_tool_schema
                    }
                }
            },
            {
                "toolSpec": {
                    "name": "trackOrderTool",
                    "description": "Retrieves real-time order tracking information and detailed status updates for customer orders by order ID. Provides estimated delivery dates.",
                    "inputSchema": {
                        "json": get_order_tracking_schema
                    }
                }
            },
            {
                "toolSpec": {
                    "name": "getWeatherTool",
                    "description": "Get current weather information for a specified location",
                    "inputSchema": {
                        "json": get_weather_schema
                    }
                }
            },
            {
                "toolSpec": {
                    "name": "getMoodSuggestionTool",
                    "description": "Get personalized suggestions to improve mood or emotional state",
                    "inputSchema": {
                        "json": get_mood_suggestion_schema
                    }
                }
            }
        ]
    
    async def process_tool_use(self, tool_name: str, tool_use_content: Dict[str, Any]) -> Dict[str, Any]:
        """Process a tool use request and return the result."""
        tool = tool_name.lower()
        
        if tool in self.tools:
            try:
                return await self.tools[tool](tool_use_content)
            except Exception as e:
                print(f"Error processing tool {tool}: {str(e)}")
                return {"error": f"Failed to process tool: {str(e)}"}
        else:
            return {"error": f"Unknown tool: {tool}"}
    
    async def get_date_and_time(self, tool_use_content: Dict[str, Any]) -> Dict[str, Any]:
        """Get current date and time information."""
        # Get current date in PST timezone
        pst_timezone = pytz.timezone("Asia/Shanghai")
        pst_date = datetime.datetime.now(pst_timezone)
        
        return {
            "formattedTime": pst_date.strftime("%I:%M %p"),
            "date": pst_date.strftime("%Y-%m-%d"),
            "year": pst_date.year,
            "month": pst_date.month,
            "day": pst_date.day,
            "dayOfWeek": pst_date.strftime("%A").upper(),
            "timezone": "PST"
        }
    
    async def track_order(self, tool_use_content: Dict[str, Any]) -> Dict[str, Any]:
        """Track an order by ID."""
        # Extract order ID from toolUseContent
        content = tool_use_content.get("content", {})
        if isinstance(content, str):
            try:
                content_data = json.loads(content)
            except json.JSONDecodeError:
                return {"error": "Invalid content format"}
        else:
            content_data = content
            
        order_id = content_data.get("orderId", "")
        request_notifications = content_data.get("requestNotifications", False)
        
        # Convert order_id to string if it's an integer
        if isinstance(order_id, int):
            order_id = str(order_id)
            
        # Validate order ID format
        if not order_id or not isinstance(order_id, str):
            return {
                "error": "Invalid order ID format",
                "orderStatus": "",
                "estimatedDelivery": "",
                "lastUpdate": ""
            }
        
        # Create deterministic randomness based on order ID
        # This ensures the same order ID always returns the same status
        seed = int(hashlib.md5(order_id.encode(), usedforsecurity=False).hexdigest(), 16) % 10000
        random.seed(seed)
        
        # Possible statuses with appropriate weights
        statuses = [
            "Order received", 
            "Processing", 
            "Preparing for shipment",
            "Shipped",
            "In transit", 
            "Out for delivery",
            "Delivered",
            "Delayed"
        ]
        
        weights = [10, 15, 15, 20, 20, 10, 5, 3]
        
        # Select a status based on the weights
        status = random.choices(statuses, weights=weights, k=1)[0]
        
        # Generate a realistic estimated delivery date
        today = datetime.datetime.now()
        # Handle estimated delivery date based on status
        if status == "Delivered":
            # For delivered items, delivery date is in the past
            delivery_days = -random.randint(0, 3)
            estimated_delivery = (today + datetime.timedelta(days=delivery_days)).strftime("%Y-%m-%d")
        elif status == "Out for delivery":
            # For out for delivery, delivery is today
            estimated_delivery = today.strftime("%Y-%m-%d")
        else:
            # For other statuses, delivery is in the future
            delivery_days = random.randint(1, 10)
            estimated_delivery = (today + datetime.timedelta(days=delivery_days)).strftime("%Y-%m-%d")

        # Handle notification request if enabled
        notification_message = ""
        if request_notifications and status != "Delivered":
            notification_message = f"You will receive notifications for order {order_id}"

        # Return comprehensive tracking information
        tracking_info = {
            "orderStatus": status,
            "orderNumber": order_id,
            "notificationStatus": notification_message
        }

        # Add appropriate fields based on status
        if status == "Delivered":
            tracking_info["deliveredOn"] = estimated_delivery
        elif status == "Out for delivery":
            tracking_info["expectedDelivery"] = "Today"
        else:
            tracking_info["estimatedDelivery"] = estimated_delivery

        # Add location information based on status
        if status == "In transit":
            tracking_info["currentLocation"] = "Distribution Center"
        elif status == "Delivered":
            tracking_info["deliveryLocation"] = "Front Door"
            
        # Add additional info for delayed status
        if status == "Delayed":
            tracking_info["additionalInfo"] = "Weather delays possible"
            
        return tracking_info
    
    async def get_weather(self, tool_use_content: Dict[str, Any]) -> Dict[str, Any]:
        """Get simulated weather information for a location."""
        # Extract parameters
        content = tool_use_content.get("content", {})
        if isinstance(content, str):
            try:
                content_data = json.loads(content)
            except json.JSONDecodeError:
                return {"error": "Invalid content format"}
        else:
            content_data = content
            
        location = content_data.get("location", "")
        unit = content_data.get("unit", "celsius")
        
        if not location:
            return {"error": "Location is required"}
        
        # Create deterministic weather based on location
        seed = int(hashlib.md5(location.encode(), usedforsecurity=False).hexdigest(), 16) % 10000
        random.seed(seed)
        
        # Generate weather conditions
        conditions = ["Sunny", "Partly Cloudy", "Cloudy", "Rainy", "Thunderstorm", "Snowy", "Foggy", "Windy"]
        condition = random.choice(conditions)
        
        # Generate temperature based on condition
        if condition == "Sunny":
            base_temp = random.randint(25, 35)
        elif condition in ["Partly Cloudy", "Cloudy"]:
            base_temp = random.randint(18, 28)
        elif condition in ["Rainy", "Thunderstorm"]:
            base_temp = random.randint(15, 25)
        elif condition == "Snowy":
            base_temp = random.randint(-5, 5)
        elif condition == "Foggy":
            base_temp = random.randint(10, 20)
        else:  # Windy
            base_temp = random.randint(15, 25)
        
        # Convert to Fahrenheit if requested
        if unit.lower() == "fahrenheit":
            temp = round((base_temp * 9/5) + 32)
            temp_unit = "°F"
        else:
            temp = base_temp
            temp_unit = "°C"
        
        # Generate humidity and wind speed
        humidity = random.randint(30, 90)
        wind_speed = random.randint(5, 30)
        
        return {
            "location": location,
            "condition": condition,
            "temperature": temp,
            "temperatureUnit": temp_unit,
            "humidity": humidity,
            "windSpeed": wind_speed,
            "windUnit": "km/h",
            "lastUpdated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }
    
    async def get_mood_suggestion(self, tool_use_content: Dict[str, Any]) -> Dict[str, Any]:
        """Get personalized suggestions to improve mood or emotional state."""
        # Extract parameters
        content = tool_use_content.get("content", {})
        if isinstance(content, str):
            try:
                content_data = json.loads(content)
            except json.JSONDecodeError:
                return {"error": "Invalid content format"}
        else:
            content_data = content
            
        current_mood = content_data.get("currentMood", "").lower()
        intensity = content_data.get("intensity", "moderate").lower()
        
        if not current_mood:
            return {"error": "Current mood is required"}
        
        # Define mood categories and suggestions
        mood_suggestions = {
            "sad": {
                "mild": [
                    "Listen to uplifting music",
                    "Take a short walk outside",
                    "Call a friend for a quick chat"
                ],
                "moderate": [
                    "Practice mindfulness meditation for 10 minutes",
                    "Watch a comedy show or funny videos",
                    "Write down three things you're grateful for"
                ],
                "intense": [
                    "Reach out to a close friend or family member",
                    "Consider talking to a professional counselor",
                    "Practice deep breathing exercises and self-compassion"
                ]
            },
            "anxious": {
                "mild": [
                    "Take five deep breaths",
                    "Step outside for fresh air",
                    "Make a cup of calming tea"
                ],
                "moderate": [
                    "Try a guided meditation for anxiety",
                    "Write down your worries and challenge negative thoughts",
                    "Do a brief physical activity like stretching"
                ],
                "intense": [
                    "Use the 5-4-3-2-1 grounding technique",
                    "Practice progressive muscle relaxation",
                    "Consider talking to a mental health professional"
                ]
            },
            "angry": {
                "mild": [
                    "Count to ten slowly",
                    "Take a short break from the situation",
                    "Drink a glass of cold water"
                ],
                "moderate": [
                    "Do physical exercise to release tension",
                    "Write down your feelings without judgment",
                    "Listen to calming music"
                ],
                "intense": [
                    "Remove yourself from the triggering situation",
                    "Practice deep breathing until you feel calmer",
                    "Use visualization to imagine a peaceful scene"
                ]
            },
            "stressed": {
                "mild": [
                    "Take a short break and stretch",
                    "Make a to-do list to organize tasks",
                    "Listen to calming music"
                ],
                "moderate": [
                    "Go for a walk outside",
                    "Practice progressive muscle relaxation",
                    "Set boundaries and learn to say no"
                ],
                "intense": [
                    "Prioritize self-care activities",
                    "Break large tasks into smaller steps",
                    "Consider talking to someone about your stress"
                ]
            },
            "tired": {
                "mild": [
                    "Take a short 10-minute power nap",
                    "Have a healthy snack for energy",
                    "Do some light stretching"
                ],
                "moderate": [
                    "Step outside for fresh air and sunlight",
                    "Drink water as dehydration can cause fatigue",
                    "Take short breaks between tasks"
                ],
                "intense": [
                    "Evaluate your sleep schedule and quality",
                    "Consider reducing caffeine and screen time before bed",
                    "Make time for proper rest and recovery"
                ]
            },
            "happy": {
                "mild": [
                    "Share your happiness with someone else",
                    "Express gratitude for the moment",
                    "Take a photo to remember this feeling"
                ],
                "moderate": [
                    "Channel your positive energy into a creative activity",
                    "Do something kind for someone else",
                    "Journal about what made you happy"
                ],
                "intense": [
                    "Celebrate your joy fully without holding back",
                    "Use this positive state to tackle something challenging",
                    "Reflect on what led to this happiness to recreate it later"
                ]
            }
        }
        
        # Find the best matching mood category
        best_match = None
        for mood_category in mood_suggestions.keys():
            if mood_category in current_mood or current_mood in mood_category:
                best_match = mood_category
                break
        
        # If no direct match, use a default category
        if not best_match:
            if any(word in current_mood for word in ["depressed", "down", "blue", "gloomy"]):
                best_match = "sad"
            elif any(word in current_mood for word in ["worried", "nervous", "tense", "uneasy"]):
                best_match = "anxious"
            elif any(word in current_mood for word in ["mad", "frustrated", "irritated", "annoyed"]):
                best_match = "angry"
            elif any(word in current_mood for word in ["exhausted", "sleepy", "fatigued", "drained"]):
                best_match = "tired"
            elif any(word in current_mood for word in ["joyful", "excited", "pleased", "content"]):
                best_match = "happy"
            else:
                best_match = "stressed"  # Default fallback
        
        # Get suggestions for the matched mood and intensity
        if best_match in mood_suggestions and intensity in mood_suggestions[best_match]:
            suggestions = mood_suggestions[best_match][intensity]
        else:
            # Fallback to moderate intensity if specific intensity not found
            suggestions = mood_suggestions.get(best_match, mood_suggestions["stressed"])["moderate"]
        
        # Add a general suggestion based on the mood
        general_suggestions = {
            "sad": "Remember that emotions are temporary and will pass with time.",
            "anxious": "Focus on what you can control in the present moment.",
            "angry": "Try to understand the root cause of your anger before reacting.",
            "stressed": "Taking small breaks can significantly reduce overall stress levels.",
            "tired": "Listen to your body's needs for rest and recovery.",
            "happy": "Savor this positive emotion and remember what contributed to it."
        }
        
        return {
            "mood": best_match,
            "intensity": intensity,
            "suggestions": suggestions,
            "generalAdvice": general_suggestions.get(best_match, "Take care of your emotional wellbeing.")
        }
