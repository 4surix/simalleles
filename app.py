
# Python 3.8
# ----------------------------------------------------------------------------

import random
import pitwi
import cliagramme

from utils import *


def run(*args):
  pitwi.Carousel._run(*args)
  pitwi.Carousel.change(args[0], 0)
pitwi.Carousel._run = pitwi.Carousel.run
pitwi.Carousel.run = run


options = {
  'migration': 0,
  'inceste': 0,
  'taux': 1,
  'nbr_populations': 1,
  'nbr_generations': 10,
  'nbr_individus': 1000,
  'couleur': True,
  'mutation': 0,
  'selection_allele': 0,
  'avantage_allele': 0,
  'nbr_attr_attrirant': 0,
  'min_attr_attrirant': 0,
  'allow_A/A': True,
  'allow_A/a': True,
  'allow_a/a': True,
  'weigth_A': 1,
  'weigth_a': 1,
}


def update_world(indi):

  world = World({'A': options['weigth_A'], 'a': options['weigth_a']})

  NAMES = list('ABCDEFGHIJKLMN')

  for i in range(options['nbr_populations']):
    indi(f"Création des populations... {i+1}/{options['nbr_populations']}.")
    Population(
      NAMES.pop(0),
      Generation(
        count = options['nbr_individus'],
        alleles_predefinies = (
          []
          + ([('A', 'A')] if options['allow_A/A'] else [])
          + ([('A', 'a'), ('a', 'A')] if options['allow_A/a'] else [])
          + ([('a', 'a')] if options['allow_a/a'] else [])
        ) if options['allow_A/A'] + options['allow_A/a'] + options['allow_a/a'] != 3 else None
      ),
      world = world
    )

  for i in range(options['nbr_generations']):
    indi(f"Simulation des générations... {i+1}/{options['nbr_generations']}.")
    world.new_generation(
      taux = options['taux'], 
      inceste = 0 if i == 0 else options['inceste'],
      migration = 0 if i == 0 else options['migration'],
      mutation = 0 if i == 0 else options['mutation'],
    )

  return world


update_graph_pop = lambda world, name: cliagramme.baton(
    titre = "Pourcentage d'allèles par générations.",
    valeurs = {
      i: to_purcent(*calc_nbr_type_allele(gen))
      for i, gen in enumerate(world.populations[name].generations)
    },
    legende=[
      'a/a',
      'A/A',
      'A/a'
    ],
    max_valeurs_y = 16,
    couleur = options['couleur'],
    return_diagramme = True
)


pitwi.parser.file(
  'app.xml',
  variables = {
    'options': options,
    'cliagramme': cliagramme,
    'update_world': update_world,
    'update_graph_pop': update_graph_pop
  }
).run()