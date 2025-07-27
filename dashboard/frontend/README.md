# AutoPromptix Dashboard Frontend

Modern React-based frontend for the AutoPromptix dashboard, built with Vite.

## Features

- 🚀 **Fast Development**: Built with Vite for lightning-fast HMR
- ⚛️ **React 18**: Modern React with hooks and functional components
- 💅 **Styled Components**: CSS-in-JS with Emotion for component styling
- 📱 **Responsive Design**: Mobile-first design with Google Material Design principles
- 🔄 **Real-time Updates**: Auto-refresh dashboard data every 30 seconds
- 🎨 **Modern UI**: Clean, professional interface with smooth animations

## Quick Start

### Prerequisites

- Node.js 16+ 
- npm or yarn

### Installation

```bash
# Navigate to frontend directory
cd dashboard/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The development server will start on `http://localhost:3000` and automatically proxy API requests to the backend server running on port 8001.

### Building for Production

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Development

### Project Structure

```
src/
├── api/              # API communication layer
│   └── dashboard.js  # Dashboard API client
├── components/       # React components
│   ├── StatsGrid.jsx
│   ├── FunctionsTab.jsx
│   ├── TestPoolsTab.jsx
│   ├── Sidebar.jsx
│   ├── CreateTestPoolModal.jsx
│   └── TestPoolModal.jsx
├── App.jsx          # Main application component
├── main.jsx         # React entry point
└── index.css        # Global styles
```

### Key Components

- **App.jsx**: Main application container with state management
- **StatsGrid**: Dashboard statistics cards
- **FunctionsTab**: Display registered functions with metadata
- **TestPoolsTab**: Manage test data pools
- **Sidebar**: Quick actions and system information
- **Modals**: Create and view test pool details

### API Integration

The frontend communicates with the backend via RESTful API:

- `GET /api/stats` - Dashboard statistics
- `GET /api/functions` - Registered functions
- `GET /api/test-pools` - Test data pools list
- `GET /api/test-pools/{name}` - Test pool details
- `POST /api/test-pools` - Create test pool
- `DELETE /api/test-pools/{name}` - Delete test pool

### Styling

Uses Emotion CSS-in-JS for component styling with:
- Google Material Design color palette
- Consistent spacing and typography
- Smooth hover effects and transitions
- Responsive grid layouts

### State Management

React hooks for local state management:
- `useState` for component state
- `useEffect` for side effects and API calls
- Props for parent-child communication

## Commands

```bash
# Development
npm run dev          # Start dev server with HMR
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint

# Dependencies
npm install          # Install all dependencies
npm install <package> # Add new dependency
```

## Configuration

### Vite Configuration

The `vite.config.js` file includes:
- React plugin configuration
- Development server proxy to backend
- Build output configuration

### Environment Variables

Create `.env.local` for local environment variables:

```bash
VITE_API_URL=http://localhost:8001
```

## Browser Support

- Chrome 88+
- Firefox 85+
- Safari 14+
- Edge 88+

## Deployment

### With Backend Server

The backend server automatically serves the built frontend files from the `dist` directory.

1. Build the frontend: `npm run build`
2. Start the backend server
3. Access dashboard at `http://localhost:8001`

### Standalone Deployment

Deploy the `dist` folder to any static hosting service:

- Vercel
- Netlify
- AWS S3 + CloudFront
- GitHub Pages

## Contributing

1. Follow React best practices
2. Use TypeScript where beneficial
3. Maintain consistent code style
4. Add tests for new components
5. Update documentation

## Technologies

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Emotion** - CSS-in-JS styling
- **Axios** - HTTP client
- **Lucide React** - Icon library
- **ESLint** - Code linting 