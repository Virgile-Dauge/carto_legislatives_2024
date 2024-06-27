import folium

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
from io import StringIO
from geopandas import GeoDataFrame
from folium import Map

def create_pie_chart(data, colors, circo_number=None):
    fig, ax = plt.subplots(figsize=(1, 1))
    ax.pie(data, colors=colors, labels=None, radius=1, wedgeprops=dict(width=0.3, edgecolor='w'))
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.patch.set_alpha(0)
    fig.patch.set_alpha(0)
    ax.axis('equal')  # Assure que le graphique en camembert est un cercle
    if circo_number is not None:
        text = ax.text(0, 0, str(circo_number), ha='center', va='center', 
                       fontsize=22, fontweight='bold', 
                       color='white',)
        text = ax.text(0, 0, str(circo_number), ha='center', va='center', 
                       fontsize=20, fontweight='bold', 
                       color='black',)  # Ajouter le numéro de la circo au centre avec une police plus grande et en gras
    buff = StringIO()
    plt.savefig(buff, format="SVG", transparent=True)
    buff.seek(0)
    svg = buff.read().replace("\n", "")
    plt.close(fig)
    return svg

def add_pie_charts_to_map(gdf : GeoDataFrame, to_display : dict[str, str], map_obj: Map):
    columns = list(to_display.keys())
    colors = list(to_display.values())

    for idx, row in gdf.iterrows():
        centroid = row['geometry'].centroid
        data = row[columns].dropna().tolist()
        pie_chart_svg = create_pie_chart(data, colors[:len(data)], row['ci_id'][-2:])
        folium.Marker(
            location=[centroid.y, centroid.x],
            icon=folium.DivIcon(html=f'''
                <div style="position: relative; width: 0px; height: 0px;">
                    <div style="position: absolute; top: -50px; left: -50px;">
                        {pie_chart_svg}
                    </div>
                </div>
            ''')
        ).add_to(map_obj)

def create_map(bv_gdf: GeoDataFrame, ci_gdf: GeoDataFrame) -> folium.Map:

    # Calculate the centroid of the entire GeoDataFrame
    centroid = ci_gdf.unary_union.centroid
    #ci_gdf = ci_gdf.to_crs(epsg=3857)
    #bv_gdf = bv_gdf.to_crs(epsg=3857)
    # Create a map centered on the center of the department
    m = folium.Map(location=[centroid.y, centroid.x], zoom_start=11)

    # Dictionary of columns to display and their colors
    to_display = {
        '% Abstentions': 'Greys',
        'extrême droite - % Voix/inscrits': 'YlOrBr',
        'front populaire - % Voix/inscrits': 'Reds',
        'macronie - % Voix/inscrits': 'Blues',
        'divers - % Voix/inscrits': 'Purples',
        'Où parler aux électeurices du RN': 'YlOrRd',
        'Où toucher les abstentionnistes': 'OrRd'
    }

    # Convert the GeoDataFrames to JSON
    ci_json = ci_gdf.to_json()

    # Add the choropleth layers
    for column, color in to_display.items():
        show = column == 'Où toucher les abstentionnistes'
        bv_json = bv_gdf[['bv_id', 'geometry']].to_json()
        folium.Choropleth(
            geo_data=bv_json,
            data=bv_gdf[['bv_id', column]],
            columns=['bv_id', column],
            key_on='feature.properties.bv_id',
            fill_color=color,
            fill_opacity=0.6,
            line_opacity=0.7,
            show=show,
            name=f'{column}'
        ).add_to(m)

    to_display = {
        'front populaire - % Voix/inscrits': '#e60000',
        'macronie - % Voix/inscrits': '#ffcc00',
        'divers - % Voix/inscrits': '#542788',
        'extrême droite - % Voix/inscrits': '#996633',
        '% Abstentions': '#bababa',
    }
    # Create a FeatureGroup for the pie charts
    pie_chart_layer = folium.FeatureGroup(name='Camemberts')
    # Ajouter les camemberts à la carte
    add_pie_charts_to_map(ci_gdf, to_display, pie_chart_layer)
    # Add the pie chart layer to the map
    pie_chart_layer.add_to(m)
    
    # Add a layer from ci_gdf
    folium.GeoJson(
        ci_gdf,
        name='Circonscriptions',
        style_function=lambda x: {
            'fillColor': 'transparent',
            'color': 'black',
            'weight': 2,
            'fillOpacity': 0.5
        }
    ).add_to(m)
    # Créer la legende personnalisée
    legend_html = '''
    <div style="position: fixed;
                bottom: 50px; left: 50px; width: 150px; height: 200px;
                background-color: white; z-index:1000; font-size:14px;
                border:2px solid grey; border-radius:5px; padding: 10px;">
        <h4>Légende</h4>
        <i style="background: #e60000; width: 10px; height: 10px; display: inline-block;"></i> Front populaire<br>
        <i style="background: #ffcc00; width: 10px; height: 10px; display: inline-block;"></i> Macronie<br>
        <i style="background: #542788; width: 10px; height: 10px; display: inline-block;"></i> Divers (LR, AR, Animaliste, écologie au centre)<br>
        <i style="background: #996633; width: 10px; height: 10px; display: inline-block;"></i> Extrême droite<br>
        <i style="background: #bababa; width: 10px; height: 10px; display: inline-block;"></i> Abstention
    </div>
    '''

    # Ajouter une légende personnalisée à la carte
    m.get_root().html.add_child(folium.Element(legend_html))

    # Ajouter la couche de contrôle pour permettre d'activer/désactiver les couches
    folium.LayerControl().add_to(m)
    
    return m