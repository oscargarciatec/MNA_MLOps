import React, { useState } from 'react';

const API_BASE_URL = 'https://power-predictor-api-148902248893.us-east1.run.app'; 

function PredictionForm() {
    const [formData, setFormData] = useState({
        Temperature: '',
        Humidity: '',
        WindSpeed: '',
        GeneralDiffuseFlows: '',
        DiffuseFlows: '',
        Timestamp: new Date().toISOString().substring(0, 16), // YYYY-MM-DDThh:mm format for datetime-local
    });
    const [prediction, setPrediction] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);
        setPrediction(null);

        // Prepare data: convert numbers, ensure Timestamp is a valid ISO string
        const payload = {
            ...formData,
            Temperature: parseFloat(formData.Temperature),
            Humidity: parseFloat(formData.Humidity),
            WindSpeed: parseFloat(formData.WindSpeed),
            GeneralDiffuseFlows: parseFloat(formData.GeneralDiffuseFlows),
            DiffuseFlows: parseFloat(formData.DiffuseFlows),
            Timestamp: formData.Timestamp + ':00' // Append seconds to match the ISO format expected by FastAPI's datetime
        };
        
        // Basic validation (you should expand this)
        const isInvalid = Object.values(payload).some(v => v === '' || isNaN(v) && typeof v === 'number');
        if (isInvalid) {
            setError('Please enter valid numerical values for all fields.');
            setIsLoading(false);
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/predict`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            const data = await response.json();

            if (!response.ok) {
                // Handle API errors (e.g., validation, internal server error)
                setError(data.detail || 'Failed to get prediction from API.');
                setPrediction(null);
            } else {
                setPrediction(data.predicted_power_consumption_zone2.toFixed(2));
                setError(null);
            }
        } catch (err) {
            console.error('Network or parsing error:', err);
            setError('Could not connect to the prediction service.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div style={{ padding: '20px', maxWidth: '400px', margin: 'auto' }}>
            <h2>⚡ Power Consumption Zone 2 Predictor</h2>
            <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '10px' }}>
                {Object.keys(formData).map((key) => (
                    <div key={key}>
                        <label htmlFor={key} style={{ display: 'block', marginBottom: '5px' }}>
                            {key === 'Timestamp' ? 'Date & Time' : key}
                        </label>
                        <input
                            type={key === 'Timestamp' ? 'datetime-local' : 'number'}
                            name={key}
                            id={key}
                            value={formData[key]}
                            onChange={handleChange}
                            required
                            step={key === 'Timestamp' ? null : "0.01"}
                            style={{ width: '100%', padding: '8px', boxSizing: 'border-box' }}
                        />
                    </div>
                ))}
                <button type="submit" disabled={isLoading} style={{ padding: '10px', backgroundColor: '#007bff', color: 'white', border: 'none', cursor: 'pointer' }}>
                    {isLoading ? 'Predicting...' : 'Get Prediction'}
                </button>
            </form>

            {error && <p style={{ color: 'red', marginTop: '15px' }}>Error: {error}</p>}
            
            {prediction !== null && (
                <div style={{ marginTop: '20px', padding: '15px', border: '1px solid #ccc', borderRadius: '5px', backgroundColor: '#e9e9e9' }}>
                    <h3>✅ Predicted Power Consumption (Zone 2):</h3>
                    <p style={{ fontSize: '1.5em', margin: '0' }}>
                        **{prediction}**
                    </p>
                </div>
            )}
        </div>
    );
}

export default PredictionForm;