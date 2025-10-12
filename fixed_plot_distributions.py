def plot_distributions_and_outliers(df):
    # Variables numéricas
    numeric_vars = ['Temperature', 'Humidity', 'Wind Speed', 
                    'Zone 1 Power Consumption', 'Zone 2  Power Consumption', 'Zone 3  Power Consumption']
    
    # Crear figura con subplots
    fig = make_subplots(rows=len(numeric_vars), cols=2,
                        subplot_titles=([f'Distribución de {var}' for var in numeric_vars] +
                                       [f'Box Plot de {var}' for var in numeric_vars]),
                        vertical_spacing=0.05)
    
    # Agregar histogramas y box plots
    for i, var in enumerate(numeric_vars, 1):
        # Calcular límites para mejorar escala
        data = df[var].dropna()
        q1, q3 = np.percentile(data, [25, 75])
        iqr = q3 - q1
        upper_bound = q3 + 1.5 * iqr
        lower_bound = max(q1 - 1.5 * iqr, data.min())
        
        # Histograma con escala ajustada
        fig.add_trace(
            go.Histogram(
                x=df[var], 
                name=var, 
                nbinsx=30,  # Reducir número de bins para mejor visualización
                autobinx=False,  # Desactivar bins automáticos
                xbins=dict(
                    start=lower_bound,
                    end=min(upper_bound, data.quantile(0.995)),  # Limitar a 99.5% para evitar outliers extremos
                    size=(upper_bound-lower_bound)/30  # Tamaño de bin proporcional al rango
                )
            ),
            row=i, col=1
        )
        
        # Box plot
        fig.add_trace(
            go.Box(y=df[var], name=var, boxmean=True),  # Mostrar media en el boxplot
            row=i, col=2
        )
        
        # Configurar ejes para histograma
        fig.update_xaxes(
            range=[lower_bound, min(upper_bound*1.1, data.quantile(0.995))],  # Rango del eje X ajustado
            row=i, 
            col=1
        )
    
    # Actualizar layout
    fig.update_layout(
        height=300*len(numeric_vars), 
        width=1200,
        showlegend=False,
        title_text="Distribuciones y Valores Atípicos por Variable"
    )
    
    return fig