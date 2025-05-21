import React, { useState, useEffect } from "react";
import { api } from '../services/apiService';
import { Box, Typography, Grid, Card, CardContent, CardActions, Button } from '@mui/material';

export default function Home() {
  const [cars, setCars] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCars = async () => {
      try {
        const data = await api.getCars();
        setCars(data);
        setError(null);
      } catch (err) {
        setError('Failed to fetch cars. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchCars();
  }, []);

  if (loading) {
    return (
      <Box sx={{ p: 4 }}>
        <Typography>Loading cars...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 4 }}>
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 4 }}>
      <Typography variant="h4" gutterBottom>
        Available Cars
      </Typography>
      
      <Grid container spacing={3}>
        {cars.map((car) => (
          <Grid item xs={12} sm={6} md={4} key={car.id}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {car.make} {car.model}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Year: {car.year}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Price per day: ${car.price_per_day}
                </Typography>
                <Typography variant="body2" color={car.available ? 'success.main' : 'error.main'}>
                  Status: {car.available ? 'Available' : 'Rented'}
                </Typography>
              </CardContent>
              <CardActions>
                <Button size="small" color="primary">
                  Rent Now
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
