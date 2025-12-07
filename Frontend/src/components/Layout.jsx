import React, { useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  IconButton,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Avatar,
  Menu,
  MenuItem,
  Chip,
  Badge,
  Tooltip,
  Stack,
  Container,
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard,
  Search,
  Rule,
  Settings,
  Logout,
  Person,
  Notifications,
  Help,
  DarkMode,
  LightMode,
  ChevronLeft,
  ChevronRight,
  Timeline,
  Security
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { useSystem } from '../contexts/SystemContext';
import { navigationRoutes } from '../routes';

const drawerWidth = 280;

const Layout = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileOpen, setMobileOpen] = useState(false);
  const [userMenuAnchor, setUserMenuAnchor] = useState(null);
  const [notificationsAnchor, setNotificationsAnchor] = useState(null);
  
  const { user, logout } = useAuth();
  const { systemStatus, wsConnected } = useSystem();
  const navigate = useNavigate();

  const [drawerOpen, setDrawerOpen] = useState(!isMobile);

  const handleDrawerToggle = () => {
    if (isMobile) {
      setMobileOpen(!mobileOpen);
    } else {
      setDrawerOpen(!drawerOpen);
    }
  };

  const handleUserMenuOpen = (event) => {
    setUserMenuAnchor(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setUserMenuAnchor(null);
  };

  const handleLogout = () => {
    logout();
    handleUserMenuClose();
  };

  const handleNotificationClick = (event) => {
    setNotificationsAnchor(event.currentTarget);
  };

  const handleNotificationClose = () => {
    setNotificationsAnchor(null);
  };

  const drawer = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Logo and Title */}
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.3 }}
        >
          <Stack alignItems="center" spacing={1}>
            <Avatar
              sx={{
                width: 60,
                height: 60,
                bgcolor: 'primary.main',
                color: 'white',
                fontSize: '1.5rem',
                fontWeight: 'bold'
              }}
            >
              RAG
            </Avatar>
            <Typography variant="h6" fontWeight="bold" color="primary.main">
              Live Data RAG
            </Typography>
            <Typography variant="caption" color="text.secondary">
              with Actions
            </Typography>
            <Chip
              size="small"
              label={wsConnected ? 'CONNECTED' : 'DISCONNECTED'}
              color={wsConnected ? 'success' : 'error'}
              variant="outlined"
            />
          </Stack>
        </motion.div>
      </Box>

      <Divider />

      {/* Navigation Items */}
      <List sx={{ flexGrow: 1, pt: 2 }}>
        {navigationRoutes.map((route) => {
          const IconComponent = {
            dashboard: Dashboard,
            search: Search,
            rule: Rule,
            settings: Settings
          }[route.icon] || Dashboard;

          return (
            <ListItem key={route.path} disablePadding>
              <ListItemButton
                selected={window.location.pathname === route.path}
                onClick={() => {
                  navigate(route.path);
                  if (isMobile) setMobileOpen(false);
                }}
                sx={{
                  borderRadius: 2,
                  mx: 2,
                  mb: 1,
                  '&.Mui-selected': {
                    bgcolor: 'primary.light',
                    color: 'primary.contrastText',
                    '&:hover': {
                      bgcolor: 'primary.light'
                    }
                  }
                }}
              >
                <ListItemIcon>
                  <IconComponent />
                </ListItemIcon>
                <ListItemText 
                  primary={route.label} 
                  secondary={route.description}
                />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>

      {/* System Status */}
      <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 2, m: 2 }}>
        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
          System Status
        </Typography>
        <Stack spacing={1}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="caption">Active</Typography>
            <Chip
              size="small"
              label={systemStatus.isActive ? 'ONLINE' : 'PAUSED'}
              color={systemStatus.isActive ? 'success' : 'default'}
              variant="outlined"
            />
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="caption">Last Update</Typography>
            <Typography variant="caption">
              {new Date(systemStatus.lastUpdated).toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit' 
              })}
            </Typography>
          </Box>
        </Stack>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* AppBar */}
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerOpen ? drawerWidth : 0}px)` },
          ml: { sm: `${drawerOpen ? drawerWidth : 0}px` },
          bgcolor: 'background.paper',
          color: 'text.primary',
          boxShadow: 1
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>

          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            {navigationRoutes.find(r => r.path === window.location.pathname)?.label || 'Dashboard'}
          </Typography>

          {/* System Indicators */}
          <Stack direction="row" spacing={2} sx={{ mr: 3 }}>
            <Tooltip title="WebSocket Connection">
              <Badge
                color={wsConnected ? 'success' : 'error'}
                variant="dot"
                sx={{ mr: 1 }}
              >
                <Timeline />
              </Badge>
            </Tooltip>
            <Tooltip title="System Security">
              <Badge
                color="success"
                variant="dot"
              >
                <Security />
              </Badge>
            </Tooltip>
          </Stack>

          {/* Notifications */}
          <Tooltip title="Notifications">
            <IconButton onClick={handleNotificationClick} sx={{ mr: 1 }}>
              <Badge badgeContent={3} color="error">
                <Notifications />
              </Badge>
            </IconButton>
          </Tooltip>

          {/* User Menu */}
          <Tooltip title="Account settings">
            <IconButton onClick={handleUserMenuOpen} sx={{ p: 0 }}>
              <Avatar
                src={user?.avatar}
                alt={user?.name}
                sx={{ width: 40, height: 40 }}
              >
                {user?.name?.charAt(0)}
              </Avatar>
            </IconButton>
          </Tooltip>
        </Toolbar>
      </AppBar>

      {/* Drawer */}
      <Box
        component="nav"
        sx={{ width: { sm: drawerOpen ? drawerWidth : 0 }, flexShrink: { sm: 0 } }}
      >
        {/* Mobile drawer */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={() => setMobileOpen(false)}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { 
              boxSizing: 'border-box', 
              width: drawerWidth 
            },
          }}
        >
          {drawer}
        </Drawer>
        
        {/* Desktop drawer */}
        <Drawer
          variant="persistent"
          open={drawerOpen}
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { 
              boxSizing: 'border-box', 
              width: drawerWidth,
              borderRight: '1px solid',
              borderColor: 'divider'
            },
          }}
        >
          {drawer}
        </Drawer>
      </Box>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerOpen ? drawerWidth : 0}px)` },
          mt: '64px',
          transition: theme.transitions.create(['width', 'margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
        }}
      >
        <Container maxWidth="xl">
          <Outlet />
        </Container>
      </Box>

      {/* User Menu */}
      <Menu
        anchorEl={userMenuAnchor}
        open={Boolean(userMenuAnchor)}
        onClose={handleUserMenuClose}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <MenuItem onClick={() => { navigate('/settings/profile'); handleUserMenuClose(); }}>
          <Person sx={{ mr: 1 }} />
          Profile
        </MenuItem>
        <MenuItem onClick={() => { navigate('/settings/security'); handleUserMenuClose(); }}>
          <Security sx={{ mr: 1 }} />
          Security
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleLogout}>
          <Logout sx={{ mr: 1 }} />
          Logout
        </MenuItem>
      </Menu>

      {/* Notifications Menu */}
      <Menu
        anchorEl={notificationsAnchor}
        open={Boolean(notificationsAnchor)}
        onClose={handleNotificationClose}
      >
        <MenuItem onClick={handleNotificationClose}>
          No new notifications
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default Layout;