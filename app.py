import streamlit as st
import pandas as pd
import seaborn as sns
sns.set_theme(style="darkgrid")
import matplotlib.pyplot as plt

# Configuration du tableau de bord
st.set_page_config(page_title="Tableau de bord RH - Pilotage du Turnover", layout="wide")

# Titre principal
st.title("Tableau de Bord RH : Pilotage du Turnover")

# Chargement des données
def charger_donnees():
    return pd.read_csv("HR_training.csv", sep=";")

df = charger_donnees()

# Fonction pour calculer les KPIs
def calculer_kpis(df):
    total_employes = df.shape[0]
    total_depart = df[df['left'] == 1].shape[0]
    taux_turnover = (total_depart / total_employes) * 100

    salaire_moyen = df['salary'].value_counts().idxmax()

    df[["satisfaction_level", "last_evaluation"]] = df[["satisfaction_level", "last_evaluation"]].apply(lambda x: x.str.replace(",", ".").astype(float))
    satisfaction_moyenne = df['satisfaction_level'].mean()

    heures_travaillees_moy = df['average_montly_hours'].mean()

    promo_moy = df['promotion_last_5years'].mean()

    return total_employes, total_depart, taux_turnover, salaire_moyen, satisfaction_moyenne, heures_travaillees_moy, promo_moy

# Sélecteur de type de job
jobs = df['job'].unique()
job_selection = st.selectbox("Sélectionnez un type de poste", ["Tous les postes"] + list(jobs))

# Filtrer les données en fonction du job sélectionné
if job_selection != "Tous les postes":
    df = df[df['job'] == job_selection]

# Calcul des KPIs pour le dataset filtré
total_employes, total_depart, taux_turnover, salaire_moyen, satisfaction_moyenne, heures_travaillees_moy, promo_moy = calculer_kpis(df)

# Affichage des KPIs
def afficher_kpis():
    st.subheader("Indicateurs Clés de Performance (KPIs)")

    # Colonne 1 : Nombre Total d'Employés avec icône
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### 👥 Nombre d'Employés")
        st.metric(label="Employés", value=total_employes)

    # Colonne 2 : Nombre de Départs avec icône
    with col2:
        st.markdown("#### 🚶‍♂️ Nombre de Départs")
        st.metric(label="Départs", value=total_depart)

    # Colonne 3 : Taux de Turnover avec icône
    with col3:
        st.markdown("#### 🔄 Taux de Turnover (%)")
        st.metric(label="Turnover", value=f"{taux_turnover:.2f}")

    # Colonne 4 : Salaire Moyen avec icône
    col4, col5, col6 = st.columns(3)
    with col4:
        st.markdown("#### 💸 Salaire Moyen")
        st.metric(label="Salaire", value=f"{salaire_moyen}")

    # Colonne 5 : Satisfaction Moyenne avec icône
    with col5:
        st.markdown("#### 😊 Satisfaction Moyenne")
        st.metric(label="Satisfaction", value=f"{satisfaction_moyenne:.2f}")

    # Colonne 6 : Heures Moyennes par Mois avec icône
    with col6:
        st.markdown("#### ⏰ Nombre d'Heures Moyen par Mois")
        st.metric(label="Heures", value=f"{heures_travaillees_moy:.1f}")

# Sidebar pour les options d'analyse
st.sidebar.header("Options d'analyse")

# Aperçu des données
#if st.sidebar.checkbox("Afficher l'aperçu des données"):
#    st.subheader("Aperçu des Données")
#    st.write("**Dimensions du dataset :**", df.shape)
#    st.dataframe(df.head())

# Visualisations sur le turnover
if st.sidebar.checkbox("Afficher des visualisations"):
    st.subheader("Visualisations du Turnover")

    # Créer des colonnes
    col1, col2 = st.columns(2)  # 3 colonnes pour 3 graphiques

    # Turnover par département
    with col1:
        fig2, ax2 = plt.subplots(figsize=(7, 5))
        st.markdown("#### Turnover par Département")
        sns.countplot(x='job', hue='left', data=df, ax=ax2)
        #ax2.set_title("Turnover par Département")
        ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45)
        plt.tight_layout()
        st.pyplot(fig2)

    # Répartition du turnover
    with col2:
        fig1, ax1 = plt.subplots(figsize=(7, 5))
        st.markdown("#### Départs en fonction de la Satisfaction et l'Évaluation")
        sns.scatterplot(x='satisfaction_level', y='last_evaluation', hue='left', data=df, ax=ax1)
        plt.tight_layout()
        st.pyplot(fig1)

    col3, col4 = st.columns(2)

    with col3:
        fig2, ax2 = plt.subplots(figsize=(7, 5))
        st.markdown("#### Départs en fonction de la charge de travail")
        sns.barplot(x='number_project', y='average_montly_hours', hue='left', data=df, ax=ax2)
        ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45)
        plt.tight_layout()
        st.pyplot(fig2)

    with col4:
        fig3, ax3 = plt.subplots(figsize=(7, 5))
        st.markdown("#### Impact de la Charge de Travail sur l'Évaluation de performance et les Départs")
        sns.scatterplot(x='average_montly_hours', y='last_evaluation', hue='left', data=df, ax=ax2)
        plt.tight_layout()
        st.pyplot(fig3)


# Afficher les KPIs
afficher_kpis()

# Footer
st.sidebar.markdown("---")
st.sidebar.text("Tableau de bord RH")
