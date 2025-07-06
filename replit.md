# LandscapePro - Landscaping Workforce Management System

## Overview

LandscapePro is a comprehensive workforce management web application designed specifically for landscaping teams. Built with Flask and SQLAlchemy, it provides essential tools for task management, time tracking, team communication, and schedule coordination. The system is designed with a mobile-first approach to accommodate outdoor workers who need access to the system while on job sites.

## System Architecture

### Backend Framework
- **Flask**: Lightweight Python web framework chosen for rapid development and simplicity
- **Flask-SQLAlchemy**: ORM for database operations with automatic table creation
- **Flask-Login**: User session management and authentication
- **Flask-Dance**: OAuth integration for Replit authentication

### Frontend Technology
- **Bootstrap 5**: Responsive UI framework with dark theme support
- **Feather Icons**: Clean, minimal icon set for consistent visual design
- **Vanilla JavaScript**: Custom functionality without heavy framework dependencies

### Authentication System
- **Replit OAuth**: Primary authentication provider using Flask-Dance
- **Custom User Management**: Role-based access with worker/supervisor/manager hierarchy
- **Session Management**: Persistent login sessions with secure token storage

## Key Components

### User Management
- **User Model**: Core user entity with role-based permissions (worker, supervisor, manager)
- **OAuth Model**: Handles Replit authentication tokens and browser session management
- **Profile System**: User profiles with contact information and employment details

### Task Management
- **Task Assignment**: Tasks can be assigned to specific users with due dates and priorities
- **Status Tracking**: Tasks progress through pending, in-progress, and completed states
- **Real-time Updates**: Dashboard shows today's tasks and upcoming deadlines

### Time Tracking
- **Clock In/Out**: Simple time tracking with timestamp recording
- **Break Management**: Separate tracking for break periods
- **Location Awareness**: System designed to potentially integrate GPS location data

### Communication System
- **Message Broadcasting**: Team-wide announcements and communications
- **Message Types**: Support for urgent alerts, general announcements, and standard messages
- **Real-time Notifications**: Recent messages displayed on dashboard

### Leave Management
- **Leave Requests**: Workers can submit vacation, sick leave, and personal day requests
- **Request Types**: Categorized leave types (vacation, sick, personal, emergency)
- **Approval Workflow**: Structured approval process for supervisors/managers

## Data Flow

### Authentication Flow
1. User accesses application
2. Redirected to Replit OAuth if not authenticated
3. OAuth callback creates or updates user record
4. Session established with persistent login

### Task Assignment Flow
1. Supervisor/Manager creates tasks
2. Tasks assigned to specific workers
3. Workers view tasks on dashboard and task list
4. Status updates tracked in real-time

### Time Tracking Flow
1. Worker clocks in at start of work
2. System records timestamp and location (if available)
3. Break periods tracked separately
4. Clock out completes the work session

## External Dependencies

### Core Dependencies
- **Flask ecosystem**: Flask, Flask-SQLAlchemy, Flask-Login, Flask-Dance
- **Database**: SQLAlchemy ORM with support for SQLite/PostgreSQL
- **Authentication**: JWT tokens, OAuth2 (Replit provider)
- **Frontend**: Bootstrap 5 CDN, Feather Icons CDN

### Database Schema
- Users table with role-based access control
- OAuth table for authentication token management
- Tasks table with assignment and status tracking
- Time entries for clock in/out functionality
- Messages for team communication
- Leave requests for time-off management

## Deployment Strategy

### Replit Environment
- **Development Setup**: Configured for Replit's hosting environment
- **Environment Variables**: SESSION_SECRET and DATABASE_URL for configuration
- **Proxy Configuration**: ProxyFix middleware for HTTPS URL generation
- **Database Initialization**: Automatic table creation on startup

### Production Considerations
- **Database**: Currently supports SQLite for development, PostgreSQL for production scaling
- **Security**: Session management with secure secret keys
- **Logging**: Debug logging enabled for development environment

## Changelog
- July 06, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.