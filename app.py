import streamlit as st
import pandas as pd
import plotly.express as px

# Configuration du tableau de bord
st.set_page_config(page_title="Tableau de bord RH - Pilotage du Turnover", layout="wide")

# Titre principal
st.title("Tableau de Bord RH : Pilotage du Turnover")

# Chargement des données
def charger_donnees():
    return pd.read_csv("HR_training.csv", sep=";")

df = charger_donnees()

# IMPORTANT : Convertir correctement les colonnes numériques
# Remplace les virgules par des points et convertit en float
df[["satisfaction_level", "last_evaluation"]] = (
    df[["satisfaction_level", "last_evaluation"]]
    .apply(lambda x: x.str.replace(",", ".").astype(float))
)

# Fonction pour calculer les KPIs
def calculer_kpis(df):
    total_employes = df.shape[0]
    total_depart = df[df['left'] == 1].shape[0]
    taux_turnover = (total_depart / total_employes) * 100

    # Pour le "salaire moyen", l'exemple original prenait la modalité la plus fréquente
    # (idxmax() sur la fréquence). À adapter selon votre logique.
    salaire_moyen = df['salary'].value_counts().idxmax()

    satisfaction_moyenne = df['satisfaction_level'].mean()
    heures_travaillees_moy = df['average_montly_hours'].mean()
    promo_moy = df['promotion_last_5years'].mean()

    return total_employes, total_depart, taux_turnover, salaire_moyen, satisfaction_moyenne, heures_travaillees_moy, promo_moy

# Sélecteur de type de job
jobs = df['job'].unique()
job_selection = st.selectbox("Sélectionnez un type de poste", ["Tous les postes"] + list(jobs))

# Filtrer les données en fonction du job sélectionné
df_filtre = df.copy()
if job_selection != "Tous les postes":
    df_filtre = df[df['job'] == job_selection]

# Calcul des KPIs pour le dataset filtré
(
    total_employes,
    total_depart,
    taux_turnover,
    salaire_moyen,
    satisfaction_moyenne,
    heures_travaillees_moy,
    promo_moy
) = calculer_kpis(df_filtre)

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
        st.markdown("#### 💸 Salaire (Modalité la plus fréquente)")
        st.metric(label="Salaire", value=f"{salaire_moyen}")

    with col5:
        st.markdown("#### 😊 Satisfaction Moyenne")
        st.metric(label="Satisfaction", value=f"{satisfaction_moyenne:.2f}")

    with col6:
        st.markdown("#### ⏰ Nombre d'Heures Moyen par Mois")
        st.metric(label="Heures", value=f"{heures_travaillees_moy:.1f}")

# Sidebar pour les options d'analyse
st.sidebar.header("Options d'analyse")

# Exemple d'aperçu des données (décommenter si besoin)
# if st.sidebar.checkbox("Afficher l'aperçu des données"):
#     st.subheader("Aperçu des Données")
#     st.write("**Dimensions du dataset :**", df_filtre.shape)
#     st.dataframe(df_filtre.head())

# Visualisations sur le turnover avec Plotly
if st.sidebar.checkbox("Afficher des visualisations"):
    st.subheader("Visualisations du Turnover")

    col1, col2 = st.columns(2)

    # 1) Turnover par département (countplot -> histogram)
    with col1:
        st.markdown("#### Turnover par Département")
        fig_turnover_dept = px.histogram(
            df_filtre,
            x="job",
            color="left",
            barmode="group",
            title="Turnover par Département"
        )
        # Rotation de l'axe X si nécessaire
        fig_turnover_dept.update_layout(xaxis={'tickangle': -45})
        st.plotly_chart(fig_turnover_dept)

    # 2) Départs en fonction de la satisfaction et de l'évaluation
    with col2:
        st.markdown("#### Départs en fonction de la Satisfaction et de l'Évaluation")
        fig_satisfaction_eval = px.scatter(
            df_filtre,
            x="satisfaction_level",
            y="last_evaluation",
            color="left",
            title="Satisfaction vs. Évaluation"
        )
        st.plotly_chart(fig_satisfaction_eval)

    col3, col4 = st.columns(2)

    # 3) Départs en fonction de la charge de travail (barplot)
    with col3:
        st.markdown("#### Départs en fonction de la charge de travail")
        fig_charge = px.bar(
            df_filtre,
            x="number_project",
            y="average_montly_hours",
            color="left",
            barmode="group",
            title="Projets vs. Heures mensuelles"
        )
        st.plotly_chart(fig_charge)

    # 4) Impact de la charge de travail sur l'évaluation de performance et les départs
    with col4:
        st.markdown("#### Impact de la Charge de Travail sur l'Évaluation de performance et les Départs")
        fig_workload_eval = px.scatter(
            df_filtre,
            x="average_montly_hours",
            y="last_evaluation",
            color="left",
            title="Heures mensuelles vs. Évaluation"
        )
        st.plotly_chart(fig_workload_eval)

# Afficher les KPIs
afficher_kpis()

# Footer
st.sidebar.markdown("---")
st.sidebar.text("Tableau de bord RH")
