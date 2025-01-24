import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# Configuration du tableau de bord
st.set_page_config(page_title="Tableau de bord RH - Pilotage du Turnover", layout="wide")

# Titre principal
st.title("Tableau de Bord RH : Pilotage du Turnover")

# Chargement des données
def charger_donnees():
    return pd.read_csv("HR_training.csv", sep=";")

df = charger_donnees()

# -------------------------------------------------------------------
# Pré-traitement : conversion des colonnes satisfaction_level et last_evaluation
# en float (remplacement de virgule par un point si nécessaire).
# -------------------------------------------------------------------
df[["satisfaction_level", "last_evaluation"]] = df[["satisfaction_level", "last_evaluation"]].apply(
    lambda x: x.str.replace(",", ".").astype(float)
)

# Fonction pour calculer les KPIs
def calculer_kpis(dataframe):
    total_employes = dataframe.shape[0]
    total_depart = dataframe[dataframe['left'] == 1].shape[0]
    taux_turnover = (total_depart / total_employes) * 100

    # Salaire moyen (attention : ici c'est la modalité la plus fréquente, pas la moyenne arithmétique)
    salaire_moyen = dataframe['salary'].value_counts().idxmax()

    satisfaction_moyenne = dataframe['satisfaction_level'].mean()
    heures_travaillees_moy = dataframe['average_montly_hours'].mean()
    promo_moy = dataframe['promotion_last_5years'].mean()

    return total_employes, total_depart, taux_turnover, salaire_moyen, satisfaction_moyenne, heures_travaillees_moy, promo_moy

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

# -- Option d'afficher des visualisations
if st.sidebar.checkbox("Afficher des visualisations"):
    st.subheader("Visualisations du Turnover (Plotly)")

    # ----------------------------------------------------------------
    # 1) Turnover par Job (équivalent Seaborn countplot -> px.histogram)
    # ----------------------------------------------------------------
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

    # ----------------------------------------------------------------
    # 2) Départs en fonction de la Satisfaction et l'Évaluation
    #    (équivalent Seaborn scatterplot -> px.scatter)
    # ----------------------------------------------------------------
    fig_scatter = px.scatter(
        df_filtered,
        x='satisfaction_level',
        y='last_evaluation',
        color='left',
        title="Départs en fonction de la Satisfaction et de l'Évaluation",
        labels={'satisfaction_level': 'Satisfaction', 'last_evaluation': 'Évaluation'}
    )

    # ----------------------------------------------------------------
    # 3) Départs en fonction du nombre de projets et des heures
    #    (équivalent Seaborn barplot -> px.bar)
    # ----------------------------------------------------------------
    # On peut utiliser groupby ou directement px.bar en précisant x=, y=, color= et l'agrégation
    # Pour se rapprocher du barplot moyen, on peut faire un groupby avant.
    df_bar = df_filtered.groupby(['number_project', 'left'])['average_montly_hours'].mean().reset_index()
    fig_bar = px.bar(
        df_bar,
        x='number_project',
        y='average_montly_hours',
        color='left',
        barmode='group',
        title="Départs en fonction du nombre de projets et de la charge de travail moyenne",
        labels={'number_project': 'Nombre de projets', 'average_montly_hours': 'Heures moyennes'}
    )

    # ----------------------------------------------------------------
    # 4) Impact de la Charge de Travail sur l'Évaluation de performance et les Départs
    #    (équivalent Seaborn scatterplot -> px.scatter)
    # ----------------------------------------------------------------
    fig_scatter_eval = px.scatter(
        df_filtered,
        x='average_montly_hours',
        y='last_evaluation',
        color='left',
        title="Impact de la Charge de Travail sur l'Évaluation de performance et les Départs",
        labels={'average_montly_hours': 'Heures mensuelles', 'last_evaluation': 'Évaluation'}
    )

    # Mise en page des graphiques sur 2 colonnes
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

    # ----------------------------------------------------------------
    # 5) Graphique en courbe (Plotly) : moyenne de la satisfaction
    #    en fonction des heures de travail, de l'ancienneté et de l'évaluation
    # ----------------------------------------------------------------

    st.subheader("Satisfaction moyenne par Heures de travail, Ancienneté et Évaluation (courbes)")

    # Pour tracer 3 courbes distinctes sur un même figure, on peut utiliser make_subplots.
    # On va binner (discrétiser) les variables continues (heures de travail, évaluation).
    # L'ancienneté (time_spend_company) est déjà discrète (1,2,3,...).

    # A) Satisfaction vs heures de travail
    df_hours = df_filtered.copy()
    # On crée des bins de 20h en 20h (par exemple)
    df_hours['hours_bin'] = pd.cut(df_hours['average_montly_hours'], bins=range(80, 331, 20), right=False)
    df_hours_grouped = df_hours.groupby('hours_bin')['satisfaction_level'].mean().reset_index()

    # B) Satisfaction vs ancienneté
    df_seniority = df_filtered.groupby('time_spend_company')['satisfaction_level'].mean().reset_index()

    # C) Satisfaction vs évaluation
    df_eval = df_filtered.copy()
    # On crée 5 bins (0.0 à 1.0)
    df_eval['eval_bin'] = pd.cut(df_eval['last_evaluation'], bins=[0,0.2,0.4,0.6,0.8,1.0], right=False)
    df_eval_grouped = df_eval.groupby('eval_bin')['satisfaction_level'].mean().reset_index()

    # Construction de la figure en sous-graphes
    fig_curves = make_subplots(
        rows=1, cols=3,
        subplot_titles=(
            "Satisfaction vs Heures de travail",
            "Satisfaction vs Ancienneté",
            "Satisfaction vs Évaluation"
        )
    )

    # Trace 1 : Heures de travail
    fig_curves.add_trace(
        go.Scatter(
            x=df_hours_grouped['hours_bin'].astype(str),
            y=df_hours_grouped['satisfaction_level'],
            mode='lines+markers',
            name='Heures'
        ),
        row=1, col=1
    )

    # Trace 2 : Ancienneté
    fig_curves.add_trace(
        go.Scatter(
            x=df_seniority['time_spend_company'],
            y=df_seniority['satisfaction_level'],
            mode='lines+markers',
            name='Ancienneté'
        ),
        row=1, col=2
    )

    # Trace 3 : Évaluation
    fig_curves.add_trace(
        go.Scatter(
            x=df_eval_grouped['eval_bin'].astype(str),
            y=df_eval_grouped['satisfaction_level'],
            mode='lines+markers',
            name='Évaluation'
        ),
        row=1, col=3
    )

    fig_curves.update_layout(
        title_text="Satisfaction moyenne en fonction de différents facteurs",
        height=500
    )

    st.plotly_chart(fig_curves, use_container_width=True)

# Afficher les KPIs (en bas ou en haut selon votre préférence)
afficher_kpis()

# Footer
st.sidebar.markdown("---")
st.sidebar.text("Tableau de bord RH")
