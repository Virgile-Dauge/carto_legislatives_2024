import numpy as np
from pandas import DataFrame, Series
from geopandas import GeoDataFrame

# Fonction pour normaliser les valeurs d'une colonne par circonscription
def normalize_by_circo(votes_gdf, circo_gdf, columns):
    votes_gdf = votes_gdf.copy()
    for column in columns:
        votes_gdf[f'{column}_normalized'] = 0  # Initialiser avec des zéros pour éviter les NaN

        for _, circo in circo_gdf.iterrows():
            # Utiliser l'intersection pour obtenir les points de vote dans la circonscription
            circo_votes_gdf = votes_gdf[votes_gdf.intersects(circo.geometry)]
            if not circo_votes_gdf.empty:
                min_val = circo_votes_gdf[column].min()
                max_val = circo_votes_gdf[column].max()
                if min_val != max_val:  # Eviter la division par zéro
                    votes_gdf.loc[circo_votes_gdf.index, f'{column}_normalized'] = (
                        (circo_votes_gdf[column] - min_val) / (max_val - min_val)
                    )
                else:
                    votes_gdf.loc[circo_votes_gdf.index, f'{column}_normalized'] = 0  # Si tous les valeurs sont les mêmes, normaliser à 0

    return votes_gdf

def coude_a_coude_model(x : Series, y : Series) -> Series:
    return (1-(x-y)**2*(x*(1-y)+y*(1-x)))**500

def low_pass_model(x : Series, quantile : float, pow : int=10) -> Series:
    threshold = x.quantile(quantile)
    rate = np.minimum(np.maximum(x + (1-threshold), 0), 1)
    return Series(np.sqrt(1-(rate)**pow))

def compute_feature(bv_gdf: GeoDataFrame, ci_gdf: GeoDataFrame, alpha: float, beta: float, gamma: float, delta: float) -> Series:
    bv_gdf = bv_gdf.copy()
    bv_gdf['abstension_rate'] = bv_gdf['% Abstentions'] / 100

    bv_gdf['ed_rate'] = bv_gdf['extrême droite - % Voix/inscrits'] / 100
    bv_gdf['trop_ed'] = low_pass_model(bv_gdf['ed_rate'], quantile=0.95)


    # Utilisation de l'algèbre linéaire pour calculer les résultats
    ci_gdf['max_M_E'] = np.maximum(ci_gdf['macronie - % Voix/inscrits'], ci_gdf['extrême droite - % Voix/inscrits']) / 100
    ci_gdf['fp_rate'] = ci_gdf['front populaire - % Voix/inscrits'] / 100
    ci_gdf['cac'] = coude_a_coude_model(ci_gdf['max_M_E'], ci_gdf['fp_rate'])

    # Création d'une colonne pour les résultats dans bv_gdf
    bv_gdf['cac_circo'] = 0

    # Application des résultats de chaque circonscription aux bureaux de vote correspondants
    for idx, circo in ci_gdf.iterrows():
        circo_votes_gdf = bv_gdf[bv_gdf.intersects(circo.geometry)]
        bv_gdf.loc[circo_votes_gdf.index, 'cac_circo'] = circo['cac']

    return Series(alpha * bv_gdf['abstension_rate']
            + beta * bv_gdf['ed_rate']
            + gamma * bv_gdf['cac_circo']
            + delta * bv_gdf['trop_ed']) / (alpha + beta + gamma + delta)
    

def compute_features(bv_gdf : GeoDataFrame, ci_gdf : GeoDataFrame) -> GeoDataFrame:

    bv_gdf = bv_gdf.copy()
    bv_gdf['abstension_rate'] = bv_gdf['% Abstentions']/100
   
    seuil_fief_ed = bv_gdf['extrême droite - % Voix/inscrits'].quantile(0.95)/100
    taux = np.minimum(np.maximum(bv_gdf['extrême droite - % Voix/inscrits']/100 + (1-seuil_fief_ed), 0), 1)
    bv_gdf['trop_ed'] = np.sqrt(1-(taux)**10)

    #bv_gdf['trop_ed'] = low_pass_model(bv_gdf['extrême droite - % Voix/inscrits'])
    #bv_gdf['trop_ed'] = (1-bv_gdf['extrême droite - % Voix/inscrits']/100)
    bv_gdf['ed_rate'] = bv_gdf['extrême droite - % Voix/inscrits']/100

    bv_gdf['cac_circo'] = 0
    bv_gdf['ed_circo'] = 0
    bv_gdf['fp_circo'] = 0

    for i, circo in ci_gdf.iterrows():
        circo_votes_gdf = bv_gdf[bv_gdf.intersects(circo.geometry)]
        result_test = []
        #ed = []
        #fp = []
        for j, row in circo_votes_gdf.iterrows():
            #ed.append(row['macronie - % Voix/inscrits']+row['extrême droite - % Voix/inscrits'])
            #fp.append(row['front populaire - % Voix/inscrits'])

            # Calculate the sum of 'macronie - % Voix/inscrits' and 'divers - % Voix/inscrits'
            sum_M = circo['macronie - % Voix/inscrits']# + circo['divers - % Voix/inscrits']

            # Calculate the sum of 'extrême droite - % Voix/inscrits' and 'divers - % Voix/inscrits'
            sum_E = circo['extrême droite - % Voix/inscrits']# + circo['divers - % Voix/inscrits']

            # Find the maximum value between these sums
            max_value = np.maximum(sum_M, sum_E)
            result_test.append(coude_a_coude_model(max_value/100, circo['front populaire - % Voix/inscrits']/100))

        bv_gdf.loc[circo_votes_gdf.index, 'cac_circo'] = result_test
        #bv_gdf.loc[circo_votes_gdf.index, 'ed_circo'] = ed
        #bv_gdf.loc[circo_votes_gdf.index, 'fp_circo'] = fp

    alpha = 1
    beta = 6
    gamma = 2
    delta = 6
    # Si l'objectif est de convertir des ED alors gamma doit valoir 2 fois alpha ou beta et alpha = beta.
    bv_gdf['Où parler aux électeurices du RN'] = (alpha*bv_gdf['abstension_rate']
                                                  +beta*bv_gdf['ed_rate']
                                                  +gamma*bv_gdf['cac_circo']
                                                  +delta*bv_gdf['trop_ed']) / (alpha+beta+gamma+delta)

    alpha = 6
    beta = 1
    gamma = 2
    delta = 3
    bv_gdf['Où toucher les abstentionnistes'] = (alpha*bv_gdf['abstension_rate']
                                                 +beta*bv_gdf['ed_rate']
                                                 +gamma*bv_gdf['cac_circo']
                                                 +delta*bv_gdf['trop_ed']) / (alpha+beta+gamma+delta)
    
    return bv_gdf
