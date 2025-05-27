import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  LinearProgress,
  Alert,
  Grid,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Chip
} from '@mui/material';
import {
  CloudUpload,
  CheckCircle,
  Error,
  Info,
  Delete
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import HealthAnalyticsAPI from '../../services/api';
import { HealthDataUpload } from '../../types/health';
import { formatDisplayDateTime } from '../../utils/helpers';

const VisuallyHiddenInput = styled('input')({
  clip: 'rect(0 0 0 0)',
  clipPath: 'inset(50%)',
  height: 1,
  overflow: 'hidden',
  position: 'absolute',
  bottom: 0,
  left: 0,
  whiteSpace: 'nowrap',
  width: 1,
});

const UploadView: React.FC = () => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [message, setMessage] = useState<{ type: 'success' | 'error' | 'info', text: string } | null>(null);
  const [uploads, setUploads] = useState<HealthDataUpload[]>([]);

  React.useEffect(() => {
    loadUploads();
  }, []);

  const loadUploads = async () => {
    try {
      const response = await HealthAnalyticsAPI.getUploads();
      setUploads(response.results);
    } catch (error) {
      console.error('Failed to load uploads:', error);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.name.endsWith('.xml') && !file.name.endsWith('.zip')) {
      setMessage({
        type: 'error',
        text: 'Please select a valid Apple Health export file (.xml or .zip)'
      });
      return;
    }

    try {
      setUploading(true);
      setUploadProgress(0);
      setMessage({ type: 'info', text: 'Uploading file...' });

      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90));
      }, 200);

      const upload = await HealthAnalyticsAPI.uploadHealthData(file);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      setMessage({
        type: 'success',
        text: `File uploaded successfully! Processing ${upload.total_records} records.`
      });
      
      // Reload uploads list
      await loadUploads();
      
      // Reset form
      event.target.value = '';
      
    } catch (error: any) {
      setMessage({
        type: 'error',
        text: error.response?.data?.message || 'Upload failed. Please try again.'
      });
    } finally {
      setUploading(false);
      setTimeout(() => {
        setUploadProgress(0);
        setMessage(null);
      }, 3000);
    }
  };

  const getStatusChip = (upload: HealthDataUpload) => {
    if (upload.processed) {
      return <Chip icon={<CheckCircle />} label="Processed" color="success" size="small" />;
    } else if (upload.error_message) {
      return <Chip icon={<Error />} label="Error" color="error" size="small" />;
    } else {
      return <Chip label="Processing" color="warning" size="small" />;
    }
  };

  return (
    <Box p={3}>
      <Typography variant="h4" fontWeight="bold" mb={3}>
        Upload Health Data
      </Typography>

      <Grid container spacing={3}>
        {/* Upload Section */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Upload Apple Health Export
            </Typography>
            <Typography variant="body2" color="text.secondary" mb={3}>
              Export your health data from the Apple Health app and upload the XML file here.
              The system will automatically process and analyze your health metrics.
            </Typography>

            <Box textAlign="center" mb={3}>
              <Button
                component="label"
                variant="contained"
                startIcon={<CloudUpload />}
                disabled={uploading}
                size="large"
              >
                Choose File
                <VisuallyHiddenInput
                  type="file"
                  accept=".xml,.zip"
                  onChange={handleFileUpload}
                />
              </Button>
            </Box>

            {uploading && (
              <Box mb={2}>
                <LinearProgress variant="determinate" value={uploadProgress} />
                <Typography variant="body2" color="text.secondary" textAlign="center" mt={1}>
                  {uploadProgress}% Complete
                </Typography>
              </Box>
            )}

            {message && (
              <Alert severity={message.type} sx={{ mb: 2 }}>
                {message.text}
              </Alert>
            )}

            <Typography variant="body2" color="text.secondary">
              <strong>Supported formats:</strong> Apple Health Export XML (.xml) or ZIP files
            </Typography>
          </Paper>
        </Grid>

        {/* Instructions */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              How to Export Apple Health Data
            </Typography>
            <Box component="ol" sx={{ pl: 2 }}>
              <Typography component="li" variant="body2" mb={1}>
                Open the Apple Health app on your iPhone
              </Typography>
              <Typography component="li" variant="body2" mb={1}>
                Tap your profile picture in the top right corner
              </Typography>
              <Typography component="li" variant="body2" mb={1}>
                Scroll down and tap "Export All Health Data"
              </Typography>
              <Typography component="li" variant="body2" mb={1}>
                Choose how to share the export file
              </Typography>
              <Typography component="li" variant="body2" mb={1}>
                Save the file and upload it here
              </Typography>
            </Box>
            
            <Alert severity="info" sx={{ mt: 2 }}>
              The export may take several minutes depending on the amount of data.
              The file will be named "apple_health_export.zip".
            </Alert>
          </Paper>
        </Grid>

        {/* Upload History */}
        <Grid size={12}>
          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Upload History
            </Typography>
            
            {uploads.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                No uploads yet. Upload your first health data file to get started.
              </Typography>
            ) : (
              <List>
                {uploads.map((upload) => (
                  <ListItem key={upload.id} divider>
                    <ListItemText
                      primary={`Upload #${upload.id}`}
                      secondary={
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Uploaded: {formatDisplayDateTime(upload.upload_date)}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Records: {upload.total_records.toLocaleString()}
                          </Typography>
                          {upload.error_message && (
                            <Typography variant="body2" color="error">
                              Error: {upload.error_message}
                            </Typography>
                          )}
                        </Box>
                      }
                    />
                    <ListItemSecondaryAction>
                      {getStatusChip(upload)}
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default UploadView;
