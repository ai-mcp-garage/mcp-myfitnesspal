#!/usr/bin/env python3
"""
MyFitnessPal MCP Server

Provides tools to retrieve nutrition data, meals, exercise, macros, and water intake
from MyFitnessPal using the python-myfitnesspal library.
"""

import os
from datetime import date, datetime, timedelta
from typing import Optional
from dotenv import load_dotenv

from fastmcp import FastMCP

from api_client import MyFitnessPalClient
from utils import text_response

# Load environment variables
load_dotenv()

# Create FastMCP server
mcp = FastMCP(
    name="MyFitnessPal",
    instructions="""
        Retrieves nutrition and fitness data from MyFitnessPal.
        Requires MyFitnessPal username and password in environment variables.
        All data is returned as human-readable markdown summaries.
        Date parameters use YYYY-MM-DD format and default to today.
    """
)

# Global client instance (lazy initialization)
_client: Optional[MyFitnessPalClient] = None


def get_client() -> MyFitnessPalClient:
    """Get or create MyFitnessPal client instance"""
    global _client
    
    if _client is None:
        _client = MyFitnessPalClient()
    
    return _client


def parse_date(date_str: Optional[str]) -> date:
    """Parse date string or return today"""
    if not date_str:
        return date.today()
    
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD")


@mcp.tool
def get_daily_summary(date: Optional[str] = None):
    """
    Get daily nutrition overview: calories consumed/remaining, macro breakdown, water, and goals.
    
    Args:
        date: Date in YYYY-MM-DD format (defaults to today)
    """
    try:
        target_date = parse_date(date)
        client = get_client()
        
        # Fetch day data
        day = client.get_day(target_date)
        
        totals = day.totals
        goals = day.goals
        
        # Extract key nutrients
        calories = totals.get('calories', 0)
        carbs = totals.get('carbohydrates', 0)
        fat = totals.get('fat', 0)
        protein = totals.get('protein', 0)
        
        # Goals
        calorie_goal = goals.get('calories', 0)
        carb_goal = goals.get('carbohydrates', 0)
        fat_goal = goals.get('fat', 0)
        protein_goal = goals.get('protein', 0)
        
        # Water (library returns milliliters)
        water_ml = day.water
        water_oz = water_ml / 29.5735  # Convert ml to oz
        water_cups = water_ml / 236.588  # Convert ml to cups
        
        # Exercise summary
        exercises = day.exercises
        total_exercise_calories = 0
        total_exercise_minutes = 0
        exercise_count = 0
        
        for exercise in exercises:
            for entry in exercise.entries:
                exercise_count += 1
                nutrition = entry.nutrition_information
                total_exercise_calories += nutrition.get('calories burned', 0)
                minutes = nutrition.get('minutes')
                if minutes:
                    total_exercise_minutes += minutes
        
        # Format output
        output = f"""# Daily Summary for {target_date.strftime('%B %d, %Y')}

## Calories
- **Consumed**: {calories:.0f} kcal
- **Goal**: {calorie_goal:.0f} kcal
- **Remaining**: {calorie_goal - calories:.0f} kcal

## Macronutrients
- **Carbohydrates**: {carbs:.0f}g / {carb_goal:.0f}g
- **Fat**: {fat:.0f}g / {fat_goal:.0f}g
- **Protein**: {protein:.0f}g / {protein_goal:.0f}g

## Exercise
- **Activities**: {exercise_count}
- **Duration**: {total_exercise_minutes:.0f} minutes
- **Calories Burned**: {total_exercise_calories:.0f} kcal

## Water Intake
- **Amount**: {water_oz:.0f} oz ({water_cups:.1f} cups, {water_ml:.0f} ml)

## Status
- **Day Complete**: {'Yes' if day.complete else 'No'}
- **Meals Logged**: {len(day.meals)}
"""
        
        return text_response(output)
        
    except Exception as e:
        return text_response(f"Error retrieving daily summary: {str(e)}")


@mcp.tool
def get_daily_meals(date: Optional[str] = None):
    """
    Get detailed meal-by-meal breakdown with all foods, servings, and calories.
    
    Args:
        date: Date in YYYY-MM-DD format (defaults to today)
    """
    try:
        target_date = parse_date(date)
        client = get_client()
        
        # Fetch day data
        day = client.get_day(target_date)
        
        output = f"# Meals for {target_date.strftime('%B %d, %Y')}\n\n"
        
        if not day.meals:
            output += "No meals logged for this day.\n"
        else:
            for meal in day.meals:
                meal_totals = meal.totals
                meal_calories = meal_totals.get('calories', 0)
                
                output += f"## {meal.name}\n"
                output += f"**Total**: {meal_calories:.0f} kcal"
                
                # Show meal macros
                meal_carbs = meal_totals.get('carbohydrates', 0)
                meal_fat = meal_totals.get('fat', 0)
                meal_protein = meal_totals.get('protein', 0)
                output += f" ({meal_carbs:.0f}C / {meal_fat:.0f}F / {meal_protein:.0f}P)\n\n"
                
                if meal.entries:
                    for entry in meal.entries:
                        nutrition = entry.nutrition_information
                        
                        output += f"- **{entry.name}**\n"
                        output += f"  - Serving: {entry.quantity} {entry.unit}\n"
                        output += f"  - Calories: {nutrition.get('calories', 0):.0f} kcal\n"
                        output += f"  - Macros: "
                        output += f"{nutrition.get('carbohydrates', 0):.0f}C / "
                        output += f"{nutrition.get('fat', 0):.0f}F / "
                        output += f"{nutrition.get('protein', 0):.0f}P\n"
                    output += "\n"
                else:
                    output += "No foods logged in this meal.\n\n"
        
        return text_response(output)
        
    except Exception as e:
        return text_response(f"Error retrieving meals: {str(e)}")


@mcp.tool
def get_daily_exercise(date: Optional[str] = None):
    """
    Get exercise activities: cardio (duration, calories) and strength (sets, reps, weight).
    
    Args:
        date: Date in YYYY-MM-DD format (defaults to today)
    """
    try:
        target_date = parse_date(date)
        client = get_client()
        
        # Fetch day data
        day = client.get_day(target_date)
        exercises = day.exercises
        
        output = f"# Exercise for {target_date.strftime('%B %d, %Y')}\n\n"
        
        if not exercises:
            output += "No exercise logged for this day.\n"
        else:
            # Collect all exercise entries from all exercise categories
            all_entries = []
            for exercise in exercises:
                all_entries.extend(exercise.entries)
            
            if not all_entries:
                output += "No exercise logged for this day.\n"
            else:
                total_calories = 0
                total_minutes = 0
                
                for entry in all_entries:
                    nutrition = entry.nutrition_information
                    
                    output += f"- **{entry.name}**\n"
                    
                    # Duration
                    minutes = nutrition.get('minutes')
                    if minutes:
                        output += f"  - Duration: {minutes:.0f} minutes\n"
                        total_minutes += minutes
                    
                    # Calories burned
                    calories = nutrition.get('calories burned', 0)
                    if calories:
                        output += f"  - Calories Burned: {calories:.0f} kcal\n"
                        total_calories += calories
                    
                    output += "\n"
                
                # Summary
                output += "## Summary\n"
                if total_minutes > 0:
                    output += f"- **Total Duration**: {total_minutes:.0f} minutes\n"
                if total_calories > 0:
                    output += f"- **Total Calories Burned**: {total_calories:.0f} kcal\n"
        
        return text_response(output)
        
    except Exception as e:
        return text_response(f"Error retrieving exercise: {str(e)}")


@mcp.tool
def get_daily_macros(date: Optional[str] = None):
    """
    Get comprehensive macro and micronutrient breakdown with all tracked nutrients.
    
    Args:
        date: Date in YYYY-MM-DD format (defaults to today)
    """
    try:
        target_date = parse_date(date)
        client = get_client()
        
        # Fetch day data
        day = client.get_day(target_date)
        
        totals = day.totals
        goals = day.goals
        
        output = f"# Macros & Nutrients for {target_date.strftime('%B %d, %Y')}\n\n"
        
        # Macronutrients
        output += "## Macronutrients\n"
        
        def format_nutrient(name: str, display_name: str, unit: str = "g"):
            value = totals.get(name, 0)
            goal = goals.get(name, 0)
            if goal > 0:
                return f"- **{display_name}**: {value:.0f}{unit} / {goal:.0f}{unit} ({value/goal*100:.0f}%)\n"
            else:
                return f"- **{display_name}**: {value:.0f}{unit}\n"
        
        output += format_nutrient('calories', 'Calories', 'kcal')
        output += format_nutrient('carbohydrates', 'Carbohydrates')
        output += format_nutrient('protein', 'Protein')
        output += format_nutrient('fat', 'Fat')
        
        # Fat breakdown if available
        if 'saturated fat' in totals:
            output += f"  - Saturated: {totals.get('saturated fat', 0):.1f}g\n"
        if 'polyunsaturated fat' in totals:
            output += f"  - Polyunsaturated: {totals.get('polyunsaturated fat', 0):.1f}g\n"
        if 'monounsaturated fat' in totals:
            output += f"  - Monounsaturated: {totals.get('monounsaturated fat', 0):.1f}g\n"
        if 'trans fat' in totals:
            output += f"  - Trans: {totals.get('trans fat', 0):.1f}g\n"
        
        output += format_nutrient('fiber', 'Fiber')
        output += format_nutrient('sugar', 'Sugar')
        output += "\n"
        
        # Micronutrients
        output += "## Micronutrients\n"
        
        if 'sodium' in totals:
            output += format_nutrient('sodium', 'Sodium', 'mg')
        if 'potassium' in totals:
            output += format_nutrient('potassium', 'Potassium', 'mg')
        if 'cholesterol' in totals:
            output += format_nutrient('cholesterol', 'Cholesterol', 'mg')
        if 'vitamin a' in totals:
            output += format_nutrient('vitamin a', 'Vitamin A', '%')
        if 'vitamin c' in totals:
            output += format_nutrient('vitamin c', 'Vitamin C', '%')
        if 'calcium' in totals:
            output += format_nutrient('calcium', 'Calcium', '%')
        if 'iron' in totals:
            output += format_nutrient('iron', 'Iron', '%')
        
        return text_response(output)
        
    except Exception as e:
        return text_response(f"Error retrieving macros: {str(e)}")


@mcp.tool
def get_water_intake(date: Optional[str] = None):
    """
    Get water consumption for a specific day.
    
    Args:
        date: Date in YYYY-MM-DD format (defaults to today)
    """
    try:
        target_date = parse_date(date)
        client = get_client()
        
        # Fetch day data
        day = client.get_day(target_date)
        water_ml = day.water  # Library returns milliliters
        water_oz = water_ml / 29.5735  # Convert to ounces
        water_cups = water_ml / 236.588  # Convert to cups
        
        output = f"# Water Intake for {target_date.strftime('%B %d, %Y')}\n\n"
        
        if water_ml > 0:
            output += f"**Amount**: {water_oz:.0f} oz ({water_cups:.1f} cups / {water_ml:.0f} ml)\n"
        else:
            output += "No water intake logged for this day.\n"
        
        # Add helpful context
        output += f"\n*Recommended daily intake: 64 oz (8 cups / 2000 ml)*\n"
        
        if water_ml > 0:
            progress = (water_oz / 64) * 100
            output += f"*Progress: {progress:.0f}% of recommended amount*\n"
        
        return text_response(output)
        
    except Exception as e:
        return text_response(f"Error retrieving water intake: {str(e)}")


@mcp.tool
def get_date_range_summary(start_date: str, end_date: str):
    """
    Get aggregate nutrition data over a date range with trends and insights.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    try:
        start = parse_date(start_date)
        end = parse_date(end_date)
        
        if start > end:
            raise ValueError("Start date must be before or equal to end date")
        
        client = get_client()
        
        # Collect data for each day
        daily_data = []
        
        for day in client.get_date_range(start, end):
            totals = day.totals
            
            daily_data.append({
                'date': day.date,
                'calories': totals.get('calories', 0),
                'carbs': totals.get('carbohydrates', 0),
                'fat': totals.get('fat', 0),
                'protein': totals.get('protein', 0),
                'water_ml': day.water,  # Store as ml
                'complete': day.complete,
                'num_meals': len(day.meals),
                'num_exercises': len(day.exercises)
            })
        
        if not daily_data:
            return text_response("No data available for the specified date range.")
        
        # Calculate aggregates
        num_days = len(daily_data)
        avg_calories = sum(d['calories'] for d in daily_data) / num_days
        avg_carbs = sum(d['carbs'] for d in daily_data) / num_days
        avg_fat = sum(d['fat'] for d in daily_data) / num_days
        avg_protein = sum(d['protein'] for d in daily_data) / num_days
        avg_water_ml = sum(d['water_ml'] for d in daily_data) / num_days
        avg_water_oz = avg_water_ml / 29.5735
        
        complete_days = sum(1 for d in daily_data if d['complete'])
        days_with_exercise = sum(1 for d in daily_data if d['num_exercises'] > 0)
        
        # Format output
        output = f"# Date Range Summary\n"
        output += f"**{start.strftime('%B %d, %Y')}** to **{end.strftime('%B %d, %Y')}**\n"
        output += f"({num_days} days)\n\n"
        
        output += "## Daily Averages\n"
        output += f"- **Calories**: {avg_calories:.0f} kcal/day\n"
        output += f"- **Carbohydrates**: {avg_carbs:.0f}g/day\n"
        output += f"- **Fat**: {avg_fat:.0f}g/day\n"
        output += f"- **Protein**: {avg_protein:.0f}g/day\n"
        output += f"- **Water**: {avg_water_oz:.0f} oz/day ({avg_water_ml:.0f} ml/day)\n\n"
        
        output += "## Tracking Stats\n"
        output += f"- **Days Completed**: {complete_days}/{num_days} ({complete_days/num_days*100:.0f}%)\n"
        output += f"- **Days with Exercise**: {days_with_exercise}/{num_days} ({days_with_exercise/num_days*100:.0f}%)\n\n"
        
        output += "## Daily Breakdown\n"
        for day_data in daily_data:
            d = day_data['date']
            water_oz = day_data['water_ml'] / 29.5735
            output += f"- **{d.strftime('%Y-%m-%d')}**: "
            output += f"{day_data['calories']:.0f} kcal, "
            output += f"{day_data['carbs']:.0f}C/{day_data['fat']:.0f}F/{day_data['protein']:.0f}P, "
            output += f"{water_oz:.0f} oz water"
            
            status = []
            if day_data['complete']:
                status.append("✓")
            if day_data['num_exercises'] > 0:
                status.append(f"{day_data['num_exercises']} exercises")
            
            if status:
                output += f" [{', '.join(status)}]"
            
            output += "\n"
        
        return text_response(output)
        
    except Exception as e:
        return text_response(f"Error retrieving date range summary: {str(e)}")


def main():
    # Support both stdio and HTTP transports
    mcp_host = os.getenv("HOST", "127.0.0.1")
    mcp_port = os.getenv("PORT", None)
    
    if mcp_port:
        mcp.run(port=int(mcp_port), host=mcp_host, transport="streamable-http")
    else:
        mcp.run()    
if __name__ == "__main__":
    main()
