import {
    NotificationsActive,
    Security,
    Timeline,
    TrendingUp
} from '@mui/icons-material';
import {
    Alert,
    Box,
    Card,
    CardContent,
    Chip,
    Container,
    Grid,
    Paper,
    Typography
} from '@mui/material';

const SimpleDashboard = () => {
  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box mb={4}>
        <Typography variant="h3" component="h1" gutterBottom fontWeight="bold">
          Live Data RAG with Actions
        </Typography>
        <Typography variant="h6" color="text.secondary">
          Autonomous real-time data processing and action system
        </Typography>
      </Box>

      {/* Status Alert */}
      <Alert severity="success" sx={{ mb: 3 }}>
        <Typography variant="body1">
          ✅ Frontend is running successfully!
        </Typography>
        <Typography variant="body2" sx={{ mt: 1 }}>
          The backend needs to be running on http://localhost:8000 for full functionality.
        </Typography>
      </Alert>

      {/* Statistics Grid */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Timeline sx={{ color: '#1976d2', mr: 1 }} />
                <Typography variant="h6">Total Queries</Typography>
              </Box>
              <Typography variant="h4" fontWeight="bold">
                0
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Waiting for backend connection
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <NotificationsActive sx={{ color: '#d32f2f', mr: 1 }} />
                <Typography variant="h6">Actions</Typography>
              </Box>
              <Typography variant="h4" fontWeight="bold">
                0
              </Typography>
              <Typography variant="caption" color="text.secondary">
                No actions executed yet
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <TrendingUp sx={{ color: '#388e3c', mr: 1 }} />
                <Typography variant="h6">Data Points</Typography>
              </Box>
              <Typography variant="h4" fontWeight="bold">
                0
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Waiting for data streams
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Security sx={{ color: '#ed6c02', mr: 1 }} />
                <Typography variant="h6">System Status</Typography>
              </Box>
              <Chip 
                label="READY" 
                color="success" 
                sx={{ fontSize: '1.2rem', height: 40, color: 'white' }}
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Main Content */}
      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          <Paper sx={{ p: 3, minHeight: 400 }}>
            <Typography variant="h5" gutterBottom>
              Welcome to Live Data RAG
            </Typography>
            <Typography variant="body1" paragraph>
              This is a real-time data processing system with autonomous action capabilities.
            </Typography>
            
            <Box sx={{ mt: 3 }}>
              <Typography variant="h6" gutterBottom>
                Next Steps:
              </Typography>
              <ol>
                <li>
                  <Typography variant="body1" paragraph>
                    <strong>Start the Backend:</strong> Make sure the backend server is running on port 8000
                  </Typography>
                </li>
                <li>
                  <Typography variant="body1" paragraph>
                    <strong>Configure API Keys:</strong> Set up your OpenAI and Pinecone API keys in Backend/.env
                  </Typography>
                </li>
                <li>
                  <Typography variant="body1" paragraph>
                    <strong>Connect Data Sources:</strong> Configure financial, news, or custom data streams
                  </Typography>
                </li>
                <li>
                  <Typography variant="body1" paragraph>
                    <strong>Create Rules:</strong> Set up automation rules for real-time actions
                  </Typography>
                </li>
              </ol>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} lg={4}>
          <Paper sx={{ p: 3, minHeight: 400 }}>
            <Typography variant="h5" gutterBottom>
              System Information
            </Typography>
            
            <Box sx={{ mt: 3 }}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Frontend Status
              </Typography>
              <Chip label="Running" color="success" size="small" sx={{ mb: 2 }} />
              
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Backend Status
              </Typography>
              <Chip label="Checking..." color="warning" size="small" sx={{ mb: 2 }} />
              
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                WebSocket
              </Typography>
              <Chip label="Disconnected" color="default" size="small" sx={{ mb: 2 }} />
              
              <Typography variant="subtitle2" color="text.secondary" gutterBottom sx={{ mt: 3 }}>
                Version
              </Typography>
              <Typography variant="body2">v1.0.0</Typography>
              
              <Typography variant="subtitle2" color="text.secondary" gutterBottom sx={{ mt: 2 }}>
                Environment
              </Typography>
              <Typography variant="body2">Development</Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Footer */}
      <Box sx={{ mt: 4, textAlign: 'center' }}>
        <Typography variant="caption" color="text.secondary">
          Live Data RAG System • Built with React + FastAPI • Real-time Data Processing
        </Typography>
      </Box>
    </Container>
  );
};

export default SimpleDashboard;
