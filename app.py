import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

# Configuration du tableau de bord
st.set_page_config(page_title="Tableau de bord RH - Pilotage du Turnover", layout="wide")

# Titre principal
st.title("Tableau de Bord RH : Pilotage du Turnover")

# Chargement des données
def charger_donnees():
    return pd.read_csv("HR_training.csv", sep=";")

df = charger_donnees()

# Convertir satisfaction_level et last_evaluation en float
df[["satisfaction_level", "last_evaluation"]] = df[["satisfaction_level", "last_evaluation"]].apply(
    lambda x: x.str.replace(",", ".").astype(float)
)

# Fonction pour calculer les KPIs
def calculer_kpis(dataframe):
    total_employes = dataframe.shape[0]
    total_depart = dataframe[dataframe['left'] == 1].shape[0]
    taux_turnover = (total_depart / total_employes) * 100

    # Salaire "moyen" ici = modalité la plus fréquente
    salaire_frequent = dataframe['salary'].value_counts().idxmax()

    satisfaction_moyenne = dataframe['satisfaction_level'].mean()
    heures_travaillees_moy = dataframe['average_montly_hours'].mean()
    promo_moy = dataframe['promotion_last_5years'].mean()

    return total_employes, total_depart, taux_turnover, salaire_frequent, satisfaction_moyenne, heures_travaillees_moy, promo_moy

# Sélecteur de type de job
jobs = df['job'].unique()
job_selection = st.selectbox("Sélectionnez un type de poste", ["Tous les postes"] + list(jobs))

# Filtrer les données en fonction du job sélectionné
df_filtered = df.copy()
if job_selection != "Tous les postes":
    df_filtered = df_filtered[df_filtered['job'] == job_selection]

# Calcul des KPIs pour le dataset filtré
(
    total_employes,
    total_depart,
    taux_turnover,
    salaire_moyen,
    satisfaction_moyenne,
    heures_travaillees_moy,
    promo_moy
) = calculer_kpis(df_filtered)

# Affichage des KPIs
def afficher_kpis():
    st.subheader("Indicateurs Clés de Performance (KPIs)")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### 👥 Nombre d'Employés")
        st.metric(label="Employés", value=total_employes)

    with col2:
        st.markdown("#### 🚶‍♂️ Nombre de Départs")
        st.metric(label="Départs", value=total_depart)

    with col3:
        st.markdown("#### 🔄 Taux de Turnover (%)")
        st.metric(label="Turnover", value=f"{taux_turnover:.2f}")

    col4, col5, col6 = st.columns(3)
    with col4:
        st.markdown("#### 💸 Salaire le plus fréquent")
        st.metric(label="Salaire", value=f"{salaire_moyen}")

    with col5:
        st.markdown("#### 😊 Satisfaction Moyenne")
        st.metric(label="Satisfaction", value=f"{satisfaction_moyenne:.2f}")

    with col6:
        st.markdown("#### ⏰ Nombre d'Heures Moyen par Mois")
        st.metric(label="Heures", value=f"{heures_travaillees_moy:.1f}")

# Sidebar pour les options d'analyse
st.sidebar.header("Options d'analyse")

# --------------------------------------------------------------------------------
# VISUALISATIONS
# --------------------------------------------------------------------------------
if st.sidebar.checkbox("Afficher des visualisations"):
    st.subheader("Visualisations du Turnover")

    # 1) Turnover par Job
    fig_job = px.histogram(
        df_filtered,
        x='job',
        color='left',
        barmode='group',
        title="Turnover par Département/Job",
        labels={'job': 'Job', 'count': 'Nombre d\'employés'}
    )
    fig_job.update_layout(xaxis={'categoryorder':'total descending'})
    fig_job.update_xaxes(tickangle=45)

    # 2) Départs en fonction de la Satisfaction et l'Évaluation
    fig_scatter = px.scatter(
        df_filtered,
        x='satisfaction_level',
        y='last_evaluation',
        color='left',
        title="Départs : Satisfaction vs Évaluation",
        labels={'satisfaction_level': 'Satisfaction', 'last_evaluation': 'Évaluation'}
    )

    # 3) Départs en fonction du nombre de projets et heures moyennes
    df_bar = df_filtered.groupby(['number_project', 'left'])['average_montly_hours'].mean().reset_index()
    fig_bar = px.bar(
        df_bar,
        x='number_project',
        y='average_montly_hours',
        color='left',
        barmode='group',
        title="Nombre de projets et charge de travail (heures moyennes)",
        labels={'number_project': 'Nombre de projets', 'average_montly_hours': 'Heures moyennes'}
    )

    # 4) Impact de la charge de travail sur l'Évaluation
    fig_scatter_eval = px.scatter(
        df_filtered,
        x='average_montly_hours',
        y='last_evaluation',
        color='left',
        title="Charge de Travail vs Évaluation (Départs)",
        labels={'average_montly_hours': 'Heures mensuelles', 'last_evaluation': 'Évaluation'}
    )

    # Affichage sur 2 lignes, 2 colonnes
    col_viz1, col_viz2 = st.columns(2)
    with col_viz1:
        st.plotly_chart(fig_job, use_container_width=True)
    with col_viz2:
        st.plotly_chart(fig_scatter, use_container_width=True)

    col_viz3, col_viz4 = st.columns(2)
    with col_viz3:
        st.plotly_chart(fig_bar, use_container_width=True)
    with col_viz4:
        st.plotly_chart(fig_scatter_eval, use_container_width=True)

    # ---------------------------------------------------------------------------
    # 5) Graphique en courbe (toutes les courbes sur le MÊME graphe)
    #    - Satisfaction vs Heures de travail (binnées)
    #    - Satisfaction vs Ancienneté
    #    - Satisfaction vs Évaluation (binnée)
    #    On force la plage de l'axe Y à [0, 1].
    # ---------------------------------------------------------------------------
    st.subheader("Satisfaction moyenne en fonction de différents facteurs")

    # A) Satisfaction vs heures de travail (bins de 20h)
    df_hours = df_filtered.copy()
    df_hours['hours_bin'] = pd.cut(df_hours['average_montly_hours'], bins=range(80, 331, 20))
    df_hours_grouped = df_hours.groupby('hours_bin')['satisfaction_level'].mean().reset_index()
    # Convertir en chaîne de caractères pour l'axe X
    df_hours_grouped['hours_bin_str'] = df_hours_grouped['hours_bin'].astype(str)

    # B) Satisfaction vs ancienneté (time_spend_company)
    df_seniority = df_filtered.groupby('time_spend_company')['satisfaction_level'].mean().reset_index()
    # Convertir en str pour homogénéiser l'axe X
    df_seniority['time_spend_company_str'] = df_seniority['time_spend_company'].astype(str)

    # C) Satisfaction vs évaluation (bins de 0.2)
    df_eval = df_filtered.copy()
    df_eval['eval_bin'] = pd.cut(df_eval['last_evaluation'], bins=[0,0.2,0.4,0.6,0.8,1.0])
    df_eval_grouped = df_eval.groupby('eval_bin')['satisfaction_level'].mean().reset_index()
    df_eval_grouped['eval_bin_str'] = df_eval_grouped['eval_bin'].astype(str)

    # On va tout placer sur un même "axe X" de type 'category' en fusionnant les labels
    # pour distinguer chaque série. On peut préfixer chaque bin pour éviter les collisions.
    df_hours_grouped['x_category'] = 'Heures_' + df_hours_grouped['hours_bin_str']
    df_seniority['x_category'] = 'Ancienneté_' + df_seniority['time_spend_company_str']
    df_eval_grouped['x_category'] = 'Éval_' + df_eval_grouped['eval_bin_str']

    # Construire la figure
    fig_curves = go.Figure()

    # Trace 1 : Heures
    fig_curves.add_trace(
        go.Scatter(
            x=df_hours_grouped['x_category'],
            y=df_hours_grouped['satisfaction_level'],
            mode='lines+markers',
            name='Heures (bins)'
        )
    )

    # Trace 2 : Ancienneté
    fig_curves.add_trace(
        go.Scatter(
            x=df_seniority['x_category'],
            y=df_seniority['satisfaction_level'],
            mode='lines+markers',
            name='Ancienneté'
        )
    )

    # Trace 3 : Évaluation
    fig_curves.add_trace(
        go.Scatter(
            x=df_eval_grouped['x_category'],
            y=df_eval_grouped['satisfaction_level'],
            mode='lines+markers',
            name='Évaluation (bins)'
        )
    )

    # Mise en forme : tri du "x" pour un affichage un peu plus ordonné
    # (sinon l'ordre d'apparition sera l'ordre des dataframes)
    all_categories = list(df_hours_grouped['x_category']) + \
                     list(df_seniority['x_category']) + \
                     list(df_eval_grouped['x_category'])
    fig_curves.update_xaxes(categoryorder='array', categoryarray=all_categories)

    # Forcer la plage de y à [0,1]
    fig_curves.update_layout(
        title="Satisfaction moyenne",
        yaxis=dict(range=[0,1]),
        xaxis_title="Bins ou catégories",
        yaxis_title="Satisfaction moyenne"
    )

    st.plotly_chart(fig_curves, use_container_width=True)

# Afficher les KPIs
afficher_kpis()

# Footer
st.sidebar.markdown("---")
st.sidebar.text("Tableau de bord RH")
