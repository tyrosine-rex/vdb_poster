import streamlit as st
import utils.plots as plot
from  utils.barplot_custom import barplot_custom 
from utils.data_loader import data_loader
from utils.euclid_mds import plot_mds
from toml import load as toml_load

CONFIG = toml_load("src/config.toml")
DB_PATH = CONFIG["db"]

melted, samples, taxa = data_loader(DB_PATH)

def main():

         st.write("""
         # Exploration de données métagénomique
         Le but de cette page est de présenter différents graphique obtenue lors de l'exploration du jeu de données métagénomique.
         \\
         Vous retrouverez à chaque page un plot associé.
         Le menu a gauche montre un sommaire interactif qui redirige vers chaque plot. 
         """)

         Fig = plot.premier_plot(DB_PATH)
         st.plotly_chart(Fig)



         line = """
         Cette figure représente la quantité globale d'espece retrouvé dans chaque building.
         On observe que Ekeley semble contenir le plus d'individus.
         """

         st.write(line)


def page_2():
         ##################
         # Premier Plot : barplots de la richesse de chaque milieur
         ###################

         st.write("""
                  ### Barplot des especes présentes dans un building.
         """)

         

         building = st.radio(
         "Choisissez le building à investiguer : ",
         ('ekeley','porter','both'))

         Fig2 = plot.update_plot(building,DB_PATH)
         st.plotly_chart(Fig2)


def page_3():
         #####################
         # Second plot : Treemap
         #####################


         st.write("""
                  ### Treemap/SunBurst des especes présentes dans un building.

                  Ce plot représente hiérarchiquement chaque especes présentes dans les milieux
                  défini par l'utilisateur.
         """)

         building2 = st.radio(
         "Choisissez les buildings à investiguer : ",
         ('ekeley','porter'))

         option = st.selectbox(
         'Selectionnez une surface :',
         ('door out', 'door in', 'water','sink floor','stall out','stall in', 'toilet seat', 
         'toilet flush handle','soap dispenser'))

         option_fig = st.radio(
         'Selectionnez une figure :',
         ('sunburst','treemap'))

         Fig3 = plot.treemap_plotly(building2,option,DB_PATH,option_fig)
         st.plotly_chart(Fig3)



def page_4() :
         ###########
         # Troisieme plot : ACP
         ##########

         st.write("""
                  ### Invesitgation de la variance de chaque echantillon.
         """)

         color_acp = st.radio(
         "Choisissez par quel variables voulez vous colorier l'acp : ",
         ('SAMPLE_ID','gender','building','surface', "floor"))

         Fig4 = plot.acp(color_acp,DB_PATH)
         st.plotly_chart(Fig4)

def page_5():
         ########
         # Quatrieme plot : Heatmap
         ########

         st.write("""
                  ### Etude de la distance euclidienne entre chaque echantillon.
                  chaque echantillon est un vecteur à n° OTU dimension
         """)

         Fig5 = plot.heatmap(DB_PATH)
         st.plotly_chart(Fig5)

def page_6():
    st.write("Barplot interractif")

    sample_choice = st.radio(
        "Selectionnez une classe d'echantillon :",
        ('surface', 'gender', 'floor', 'building')
    )

    phylo_choice = st.radio(
        "Selectionnez un rang taxonomique :",
        ('phylum', 'class', '_order', 'family', 'genus', 'specie')
    )

    Fig6 = barplot_custom(melted, taxa, samples, phylo_choice, sample_choice)
    st.plotly_chart(Fig6)


def page_7():
    st.write("Multidimensional scaling base on euclidean matrix between samples")

    color_choice = st.radio(
        "Selectionnez une classe d'echantillon",
        ("surface", "gender", "floor", "building", "isFloor")
    )

    Fig7 = plot_mds(melted, samples, color_choice)
    st.plotly_chart(Fig7)



page_names_to_funcs = {
    "Main Page": main,
    "Barplot": page_2,
    "Treemap/Sunburst": page_3,
    "PCA 3D": page_4,
    "Heatmap": page_5,
    "Barplot interractif" : page_6, 
    "euclidean MDS" : page_7
}

list_page = [main,page_2,page_3,page_4,page_5]

selected_page = st.sidebar.radio("Select a page", page_names_to_funcs.keys())
page_names_to_funcs[selected_page]()

