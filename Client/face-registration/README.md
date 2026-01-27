# Employee Face Registration System

Separate frontend application for registering employees with face photos. This system integrates with the main Aegis-Ignis backend.

## Features

- Admin authentication
- Employee registration with face photos
- Camera capture or file upload
- Floor assignment
- Employee list view
- Face recognition integration

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure API URL (create `.env` file):
```env
VITE_API_URL=http://localhost:8000/api/v1
```

3. Start development server:
```bash
npm run dev
```

The app will be available at http://localhost:5174

## Usage

1. Login with admin credentials:
   - Email: admin@aegis-ignis.com
   - Password: admin123

2. Register employees:
   - Enter employee name and email
   - Select floor (optional)
   - Upload photo or capture from camera
   - Submit registration

3. View registered employees in the list

## Integration

This app uses the same backend as the main dashboard:
- Authentication endpoints
- Employee registration endpoints
- Floor management endpoints

The registered employees appear in the main dashboard for admins to see which employees are on which floors.

