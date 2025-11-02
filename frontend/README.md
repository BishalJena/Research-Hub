# Smart Research Hub - Frontend

AI-powered research platform for Andhra Pradesh researchers. Built with Next.js 15, TypeScript, and shadcn/ui.

## 🚀 Features

- **Topic Discovery** - Find trending research topics using AI-powered analysis
- **Paper Analysis** - Upload and auto-summarize research papers
- **Plagiarism Detection** - Multi-layer similarity detection with semantic analysis
- **Journal Recommendations** - Get personalized journal suggestions
- **Government Alignment** - Map research to AP Government priorities and funding
- **Impact Prediction** - Quantify real-world impact with district-level data

## 📋 Prerequisites

- Node.js 18+ and npm
- Backend API running on http://localhost:8000

## 🛠️ Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Create a `.env.local` file in the frontend directory:

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the app.

## 📁 Project Structure

```
frontend/
├── app/
│   ├── page.tsx                    # Landing page
│   ├── login/page.tsx             # Login page
│   ├── register/page.tsx          # Registration page
│   └── dashboard/
│       ├── page.tsx               # Dashboard home
│       ├── topics/page.tsx        # Topic Discovery
│       ├── papers/page.tsx        # Paper Upload & Analysis
│       ├── plagiarism/page.tsx    # Plagiarism Check
│       ├── journals/page.tsx      # Journal Recommendations
│       ├── government/page.tsx    # Government Alignment
│       └── impact/page.tsx        # Impact Prediction
├── components/
│   ├── ui/                        # shadcn/ui components
│   └── dashboard-layout.tsx       # Shared dashboard layout
├── lib/
│   ├── api-client.ts             # API service layer
│   ├── auth-context.tsx          # Authentication context
│   └── utils.ts                  # Utility functions
└── .env.local                     # Environment variables
```

## 🎨 Tech Stack

- **Framework:** Next.js 15 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS v4
- **UI Components:** shadcn/ui
- **Icons:** Lucide React
- **State Management:** React Context API
- **API Client:** Fetch API with custom client

## 🔑 Authentication

The app uses JWT-based authentication. After login, the token is stored in localStorage and automatically included in API requests.

### Protected Routes

All `/dashboard/*` routes require authentication. Unauthenticated users are redirected to `/login`.

## 📡 API Integration

All API calls are made through the centralized API client (`lib/api-client.ts`).

Example usage:

```typescript
import { apiClient } from '@/lib/api-client';

// Login
await apiClient.login(email, password);

// Get trending topics
const topics = await apiClient.getTrendingTopics({ discipline: 'Computer Science' });

// Upload paper
const result = await apiClient.uploadPaper(file);
```

## 🎯 Available Pages

### Public Pages
- `/` - Landing page with features showcase
- `/login` - User login
- `/register` - New user registration

### Dashboard Pages (Protected)
- `/dashboard` - Main dashboard with overview
- `/dashboard/topics` - Discover trending research topics
- `/dashboard/papers` - Upload and analyze research papers
- `/dashboard/plagiarism` - Check content for plagiarism
- `/dashboard/journals` - Get journal recommendations
- `/dashboard/government` - Analyze government alignment
- `/dashboard/impact` - Predict research impact

## 🔧 Development

### Run Development Server
```bash
npm run dev
```

### Build for Production
```bash
npm run build
```

### Start Production Server
```bash
npm start
```

### Lint Code
```bash
npm run lint
```

## 🌐 Backend Connection

Make sure the backend API is running before starting the frontend:

```bash
# In backend directory
cd ../backend
source venv/bin/activate
uvicorn app.main:app --reload
```

Backend will be available at: http://localhost:8000

## 🎨 UI Components

This project uses [shadcn/ui](https://ui.shadcn.com/) components. Components are located in `components/ui/`.

### Installed Components
- Button
- Card
- Input
- Label
- Textarea
- Select
- Dropdown Menu
- Avatar
- Badge
- Progress
- Tabs
- Dialog
- Alert
- Table

### Adding New Components
```bash
npx shadcn@latest add [component-name]
```

## 🚀 Deployment

### Vercel (Recommended)
1. Push code to GitHub
2. Import repository in Vercel
3. Add environment variable: `NEXT_PUBLIC_API_URL`
4. Deploy

### Other Platforms
Build the production bundle:
```bash
npm run build
npm start
```

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `http://localhost:8000/api/v1` |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is built for the AP Government Research Platform.

## 🆘 Troubleshooting

### "Failed to fetch" errors
- Ensure backend is running on http://localhost:8000
- Check CORS settings in backend
- Verify `.env.local` has correct API URL

### Authentication issues
- Clear localStorage and try logging in again
- Check if backend JWT secret is configured
- Verify token is being sent in Authorization header

### Build errors
- Delete `.next` folder and node_modules
- Run `npm install` again
- Ensure Node.js version is 18+

## 📞 Support

For issues or questions, please contact the development team.

---

Built with ❤️ for Andhra Pradesh researchers
