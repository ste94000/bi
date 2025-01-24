import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# Configuration du tableau de bord
st.set_page_config(page_title="Tableau de bord RH - Pilotage du Turnover", layout="wide")

# Titre principal
st.title("Tableau de Bord RH : Pilotage du Turnover")

# ----------------------------------------------------------------------
# 1) Chargement des données
# ----------------------------------------------------------------------
def charger_donnees():
    return pd.read_csv("HR_training.csv", sep=";")

df = charger_donnees()

# IMPORTANT : Convertir correctement les colonnes numériques
# (Remplacement de la virgule par le point pour satisfaction_level et last_evaluation)
df[["satisfaction_level", "last_evaluation"]] = (
    df[["satisfaction_level", "last_evaluation"]]
    .apply(lambda x: x.str.replace(",", ".").astype(float))
)

# ----------------------------------------------------------------------
# 2) Fonction pour calculer les KPIs
# ----------------------------------------------------------------------
def calculer_kpis(dataframe):
    total_employes = dataframe.shape[0]
    total_depart = dataframe[dataframe['left'] == 1].shape[0]
    taux_turnover = (total_depart / total_employes) * 100

    # Salaire "moyen" (ici : modalité la plus fréquente)
    salaire_moyen = dataframe['salary'].value_counts().idxmax() if not dataframe.empty else "N/A"

    satisfaction_moyenne = dataframe['satisfaction_level'].mean() if not dataframe.empty else 0
    heures_travaillees_moy = dataframe['average_montly_hours'].mean() if not dataframe.empty else 0
    promo_moy = dataframe['promotion_last_5years'].mean() if not dataframe.empty else 0

    return total_employes, total_depart, taux_turnover, salaire_moyen, satisfaction_moyenne, heures_travaillees_moy, promo_moy

# ----------------------------------------------------------------------
# 3) Sélecteurs (select_slider) pour filtrer le dataframe
# ----------------------------------------------------------------------
df_filtre = df.copy()

# a) Sélecteur pour 'job'
jobs_uniques = sorted(df['job'].unique())
job_options = ["Tous"] + jobs_uniques
job_selection = st.select_slider(
    "Sélectionnez un type de poste",
    options=job_options,
    value="Tous"  # valeur par défaut
)
if job_selection != "Tous":
    df_filtre = df_filtre[df_filtre['job'] == job_selection]

# b) Sélecteur pour 'time_spend_company'
anciennete_uniques = sorted(df['time_spend_company'].unique())
anciennete_options = ["Tous"] + anciennete_uniques
anciennete_selection = st.select_slider(
    "Sélectionnez une ancienneté (en années)",
    options=anciennete_options,
    value="Tous"
)
if anciennete_selection != "Tous":
    df_filtre = df_filtre[df_filtre['time_spend_company'] == anciennete_selection]

# c) Sélecteur pour 'average_montly_hours'
hours_uniques = sorted(df['average_montly_hours'].unique())
hours_options = ["Tous"] + hours_uniques
hours_selection = st.select_slider(
    "Sélectionnez un volume d'heures mensuelles",
    options=hours_options,
    value="Tous"
)
if hours_selection != "Tous":
    df_filtre = df_filtre[df_filtre['average_montly_hours'] == hours_selection]

# d) Sélecteur pour 'salary'
salary_uniques = sorted(df['salary'].unique())
salary_options = ["Tous"] + salary_uniques
salary_selection = st.select_slider(
    "Sélectionnez un niveau de salaire",
    options=salary_options,
    value="Tous"
)
if salary_selection != "Tous":
    df_filtre = df_filtre[df_filtre['salary'] == salary_selection]

# ----------------------------------------------------------------------
# 4) Calcul des KPIs sur le dataframe filtré
# ----------------------------------------------------------------------
(
    total_employes,
    total_depart,
    taux_turnover,
    salaire_moyen,
    satisfaction_moyenne,
    heures_travaillees_moy,
    promo_moy
) = calculer_kpis(df_filtre)

# ----------------------------------------------------------------------
# 5) Fonction d'affichage des KPIs
# ----------------------------------------------------------------------
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
        st.markdown("#### 💸 Salaire (Modalité la plus fréquente)")
        st.metric(label="Salaire", value=f"{salaire_moyen}")

    with col5:
        st.markdown("#### 😊 Satisfaction Moyenne")
        st.metric(label="Satisfaction", value=f"{satisfaction_moyenne:.2f}")

    with col6:
        st.markdown("#### ⏰ Nombre d'Heures Moyen par Mois")
        st.metric(label="Heures", value=f"{heures_travaillees_moy:.1f}")

# ----------------------------------------------------------------------
# 6) Barre latérale : options d'analyse
# ----------------------------------------------------------------------
st.sidebar.header("Options d'analyse")

# Visuels du turnover
if st.sidebar.checkbox("Afficher des visualisations"):
    st.subheader("Visualisations du Turnover")

    col1, col2 = st.columns(2)

    # 1) Turnover par département (histogram groupé)
    with col1:
        st.markdown("#### Turnover par Département (job)")
        fig_turnover_dept = px.histogram(
            df_filtre,
            x="job",
            color="left",
            barmode="group",
            title="Turnover par Département (left=0 ou 1)"
        )
        fig_turnover_dept.update_layout(xaxis={'tickangle': -45})
        st.plotly_chart(fig_turnover_dept, use_container_width=True)

    # 2) Départs en fonction de la satisfaction et de l'évaluation
    with col2:
        st.markdown("#### Départs : Satisfaction vs Évaluation")
        fig_satisfaction_eval = px.scatter(
            df_filtre,
            x="satisfaction_level",
            y="last_evaluation",
            color="left",
            title="Satisfaction vs. Évaluation"
        )
        st.plotly_chart(fig_satisfaction_eval, use_container_width=True)

    col3, col4 = st.columns(2)

    # 3) Départs en fonction de la charge de travail
    with col3:
        st.markdown("#### Départs en fonction de la charge de travail")
        fig_charge = px.bar(
            df_filtre,
            x="number_project",
            y="average_montly_hours",
            color="left",
            barmode="group",  # 2 barres côte à côte : left=0 et left=1
            title="Projets vs. Heures mensuelles",
            labels={
                "number_project": "Nombre de projets",
                "average_montly_hours": "Heures mensuelles",
                "left": "Départ"
            }
        )
        st.plotly_chart(fig_charge, use_container_width=True)

    # 4) Impact de la charge de travail sur l'évaluation de performance et les Départs
    with col4:
        st.markdown("#### Charge de Travail vs. Évaluation (Départs)")
        fig_workload_eval = px.scatter(
            df_filtre,
            x="average_montly_hours",
            y="last_evaluation",
            color="left",
            title="Heures mensuelles vs. Évaluation"
        )
        st.plotly_chart(fig_workload_eval, use_container_width=True)

# Autres visualisations : analyse de la satisfaction
if st.sidebar.checkbox("Analyse de la satisfaction"):
    st.subheader("Satisfaction moyenne par Heures, Ancienneté et Évaluation (courbes)")

    # A) Satisfaction vs heures (bins de 20h)
    df_hours = df_filtre.copy()
    df_hours['hours_bin'] = pd.cut(df_hours['average_montly_hours'], bins=range(80, 331, 20), right=False)
    df_hours_grouped = df_hours.groupby('hours_bin')['satisfaction_level'].mean().reset_index()

    # B) Satisfaction vs ancienneté
    df_seniority = df_filtre.groupby('time_spend_company')['satisfaction_level'].mean().reset_index()

    # C) Satisfaction vs évaluation (bins de 0.2)
    df_eval = df_filtre.copy()
    df_eval['eval_bin'] = pd.cut(df_eval['last_evaluation'], bins=[0,0.2,0.4,0.6,0.8,1.0], right=False)
    df_eval_grouped = df_eval.groupby('eval_bin')['satisfaction_level'].mean().reset_index()

    # Construction de la figure en sous-graphiques
    fig_curves = make_subplots(
        rows=1, cols=3,
        subplot_titles=(
            "Satisfaction vs Heures de travail",
            "Satisfaction vs Ancienneté",
            "Satisfaction vs Évaluation"
        )
    )

    # Trace 1 : Heures
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

# ----------------------------------------------------------------------
# 7) Affichage des KPIs (en bas ou en haut selon votre choix)
# ----------------------------------------------------------------------
afficher_kpis()

# Footer
st.sidebar.markdown("---")
st.sidebar.text("Tableau de bord RH")
