def plot_climate_correlations(df):
    # Variables climáticas
    climate_vars = ['Temperature', 'Humidity', 'Wind Speed', 'general diffuse flows', 'diffuse flows']
    consumption_vars = ['Zone 1 Power Consumption', 'Zone 2  Power Consumption', 'Zone 3  Power Consumption']
    
    # Calcular correlaciones
    corr_matrix = df[climate_vars + consumption_vars].corr()
    
    # Crear heatmap con plotly - Mejorando visibilidad y escala de colores
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu_r',  # Escala invertida para mejor visualización
        zmin=-1, zmax=1,
        text=np.around(corr_matrix, decimals=2),  # Mostrar valores numéricos
        hoverinfo='text',
        texttemplate='%{text:.2f}'  # Formato de texto para los valores
    ))
    
    # Mejorar layout para mejor visualización
    fig.update_layout(
        title='Matriz de Correlación: Variables Climáticas vs Consumo',
        height=800,
        width=1000,
        xaxis=dict(tickangle=-45),  # Rotar etiquetas para mejor lectura
        margin=dict(l=50, r=50, t=100, b=150)  # Aumentar márgenes para las etiquetas
    )
    
    return fig

# Generar y mostrar matriz de correlación
correlation_matrix = plot_climate_correlations(df)
correlation_matrix.show()