# Quick Start - Grace Modern UI

## Start the Application

```bash
cd frontend
npm run dev
```

Open browser: `http://localhost:5173`

## Navigation

### 5 Main Pages

1. **Chat & Collaboration** - `/` (default)
   - ChatGPT-style interface
   - Main conversation panel

2. **System Health** - `/health`
   - Live metrics and KPIs
   - System overview dashboard

3. **Tasks & Missions** - `/tasks`
   - Mission control board
   - Task management
   - Self-healing triggers

4. **Memory Explorer** - `/memory`
   - File browser
   - Upload documents
   - Knowledge insights

5. **Governance Hub** - `/governance`
   - Secrets vault
   - Approval workflows
   - Trust metrics

## Using Design System Components

### Import Components

```tsx
import { Card, CardHeader, CardContent, Button, Tag, KpiTile, Surface } from '../design-system';
```

### Examples

```tsx
// Card with header
<Card variant="bordered">
  <CardHeader>Title</CardHeader>
  <CardContent>Content here</CardContent>
</Card>

// Button
<Button variant="primary" icon={<Icon />} onClick={handleClick}>
  Click Me
</Button>

// KPI Tile
<KpiTile 
  label="Active Tasks"
  value="42"
  icon={<Activity />}
  status="success"
  trend="up"
  trendValue="+12%"
/>

// Tag
<Tag variant="success">Active</Tag>
```

## Build for Production

```bash
npm run build
```

Output: `dist/` folder

## Customize Theme

Edit `src/styles/theme.css`:

```css
:root {
  --color-accent-primary: #6366f1; /* Change primary color */
  --spacing-md: 1rem; /* Adjust spacing */
  /* ... more variables */
}
```

## Add New Page

1. Create `src/pages/NewPage.tsx`
2. Add route in `src/router.tsx`
3. Add nav item in `src/layout/SidebarNav.tsx`

## Troubleshooting

**Issue:** Blank screen
- Check browser console for errors
- Verify `npm run dev` is running
- Check `http://localhost:5173`

**Issue:** Routes not working
- Ensure RouterProvider in `main.tsx`
- Check `router.tsx` configuration

**Issue:** Styles missing
- Import `styles/theme.css` in `main.tsx`
- Check CSS variables in DevTools

## Documentation

- Full implementation: `MODERN_UI_IMPLEMENTATION.md`
- Design system: `src/design-system/`
- API integration: `src/api/`
