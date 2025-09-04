# Trip Planner Agent

A sophisticated multi-agent travel planning system that combines AI-powered backend agents with a modern web frontend for creating comprehensive travel itineraries.

## Project Overview

This project consists of two main components:

### Agent Backend (`/agent`)
A sophisticated multi-agent travel planning system built with CamelAI that simulates a collaborative planning session between:
- **Travel Guide**: Expert travel recommendations and planning
- **Traveler**: User preferences and feedback simulation  
- **Critic**: Quality assurance and plan validation
- **Organizer**: Final detailed itinerary creation

**Key Features:**
- Multi-agent collaboration using CamelAI framework
- Two-phase planning: high-level strategy + detailed execution
- Customizable AI models for different agent roles
- Comprehensive itinerary generation with accommodations, restaurants, and activities
- Cultural insights and practical logistics

**Technologies:** Python, CamelAI, OpenAI GPT models

### Frontend Demo (`/demo_frontend`)
A modern web application that provides an interactive interface for the travel planning agents.

**Key Features:**
- AI-powered chat interface for trip planning
- Interactive 3D globe for destination exploration
- Itinerary management and storage
- Real-time knowledge agent with search capabilities
- Responsive design for desktop and mobile

**Technologies:** React, TypeScript, Tailwind CSS, Vite, Globe.gl

## Quick Start

### Backend Agent Setup
```bash
cd agent
pip install -r requirements.txt
# Set up OPENAI_API_KEY in .env file
python trip_planner.py
```

### Frontend Demo Setup
```bash
cd demo_frontend
npm install
# Set up VITE_BACKEND_URL in .env file
npm run dev
```

## Architecture

The system demonstrates how multiple AI agents can work together to create comprehensive travel plans:

1. **Planning Phase**: Travel Guide, Traveler, and Critic agents collaborate to develop high-level travel strategies
2. **Execution Phase**: Organizer agent creates detailed day-by-day itineraries
3. **Frontend Interface**: Modern web app provides user-friendly interaction with the agent system

## Demo

Experience the full system at: [Trip-planner-demo](https://demo.gensee.ai/trip-planner/)

## Documentation

- **Agent Documentation**: See `/agent/README.md` for detailed backend usage and customization
- **Frontend Documentation**: See `/demo_frontend/README.md` for frontend development details

## Technologies

**Backend:** Python, CamelAI, OpenAI GPT-4o, GPT-4o-mini
**Frontend:** React, TypeScript, Tailwind CSS, Vite, Globe.gl, shadcn-ui
**Deployment:** GenseeAI platform for easy agent serving and deployment
