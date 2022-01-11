# Python 3.8
# ----------------------------------------------------------------------------

import random


class Generation:

    def __init__(
        self,
        count:int = 0,
        *,
        population = None,
        alleles_predefinies = None
    ):
        # Séparations des individus féminins et masculins
        #  dans le but d'optimiser la reproduction,
        #  cela évite de vérifier le sexe.
        self.females = []
        self.males = []

        self.population = population

        if count:
            for _ in range(count):
                if alleles_predefinies:
                    Individu(*random.choice(alleles_predefinies), generation=self)
                else:
                    Individu(generation=self)

    def __iter__(self):
        return self.individus

    @property
    def individus(self):
        for i in self.females:
            yield i
        for i in self.males:
            yield i

    def append(self, i):
        if i.sexe == 'F':
            self.females.append(i)
        if i.sexe == 'M':
            self.males.append(i)

    def remove(self, i):
        if i.sexe == 'F':
            self.females.remove(i)
        if i.sexe == 'M':
            self.males.remove(i)


class World:

    def __init__(self, weights:dict):
        self.populations = {}
        self.weights = weights

    def choice_allele(self, *alleles):
        return (
            random.choice(alleles) if self.weights == {'A': 1, 'a': 1}
            else
                random.choices(alleles, weights=[self.weights[alleles[0]], self.weights[alleles[1]]], k=1)[0]
        )

    def new_generation(
        self,
        *,
        migration:int = 0,
        mutation:int = 0,
        **kwargs
    ):

        ### Migration
        #

        if migration and len(self.populations) > 1:
            # On fait la migrations avant la reproduction
            #  de façon à être sur que toute les personnes
            #  ont migrée et seront piochées pour la reproduction.
            # Si un individu migre de A à B, puis on fait la generation
            #  de A, puis ensuite se même individue remigre de B à A,
            #  il ne sera jamais pris car A à déjà été fait.
            for pop in self.populations.values():
                pops = [p for p in self.populations.values() if p != pop]
                if not pops:
                    continue
                for i in pop.last_generation:
                    if random.randint(1, 100) <= migration:
                        new_pop = random.choice(pops)
                        i.old_population = (len(pop.generations), pop.name)
                        pop.last_generation.remove(i)
                        i.population = new_pop
                        new_pop.last_generation.append(i)

        if mutation:
            for pop in self.populations.values():
                for i in pop.last_generation:
                    if random.randint(1, 100) <= mutation:
                        if random.randint(0, 1) == 1:
                            i.allele_1 = 'A' if i.allele_1 == 'a' else 'a'
                        else:
                            i.allele_2 = 'A' if i.allele_2 == 'a' else 'a'

        #
        ###

        for pop in self.populations.values():
            pop.new_generation(**kwargs)


class Population:

    def __init__(
        self,
        name:str,
        generation:Generation = None,
        world:World = None
    ):
        self.name = name
        self.world = world
        self.generations = [generation] if generation else []

        generation.population = self
        world.populations[self.name] = self

    def new_generation(
        self,
        *,
        taux:float = 1.0,
        inceste:int = 0,
        migration:int = 0,
    ):

        children = Generation(population=self)

        individus = list(self.last_generation)

        try: individus_with_parent = set(
            individus + list(self.generations[-2])
        )
        except:
            individus_with_parent = individus

        for _ in range(int(len(individus) * taux)):

            i1 = random.choice(individus)


            ### Inceste
            #

            if (
                not inceste
                or random.randint(0, 100) > inceste
                or not i1.parents # When first generation
            ):
                if i1.sexe == 'F':
                    i2 = random.choice(i1.generation.males)
                if i1.sexe == 'M':
                    i2 = random.choice(i1.generation.females)
            else:
                family = [
                    i
                    for i in set([
                        *i1.parents,
                        *[c for p in i1.parents for c in p.children]
                    ])
                    if
                        # Permet de vérifier si une personne de sa famille est dans 
                        #  la même population que l'individu,
                        #  il ne peut pas se reproduire si elle n'est pas là.
                        i in individus_with_parent
                        and (
                            (i1.sexe == 'F' and i.sexe == 'M')
                            or
                            (i1.sexe == 'M' and i.sexe == 'F')
                        )
                ]

                if not family:
                    continue
                else:
                    i2 = random.choice(family)

            #
            ###

            i1.reproduce_with(i2, generation=children)

        self.add_generation(children)

    def add_generation(self, individus:list):
        self.generations.append(individus)

    @property
    def last_generation(self):
        return self.generations[-1]


class Individu:

    __slots__ = (
        'generation',
        'allele_1',
        'allele_2',
        'sexe',
        'parents',
        'children',
        'history',
        'population',
        'old_population'
    )

    def __init__(
        self,
        allele_1:str = None,
        allele_2:str = None,
        sexe:str = None,
        *,
        generation:Generation,
        parents:list = None
    ):

        self.generation = generation

        self.allele_1 = allele_1 or random.choice(['A', 'a'])
        self.allele_2 = allele_2 or random.choice(['A', 'a'])

        self.sexe = sexe or random.choice(['F', 'M'])

        if self.sexe == 'F':
            self.generation.females.append(self)
        if self.sexe == 'M':
            self.generation.males.append(self)

        self.parents = parents or []
        self.children = []
        self.history = []

    def reproduce_with(self, i, generation=None):

        choice_allele = self.generation.population.world.choice_allele

        child = Individu(
            choice_allele(self.allele_1, self.allele_2),
            choice_allele(i.allele_1, i.allele_2),
            generation = generation,
            parents = [self, i]
        )

        self.children.append(child)
        i.children.append(child)
        return child


def calc_nbr_type_allele(gen):

    A_A = 0
    A_a = 0
    a_A = 0
    a_a = 0

    for i in gen:
        if i.allele_1 == 'a' and i.allele_2 == 'a':
            a_a += 1
        if i.allele_1 == 'A' and i.allele_2 == 'A':
            A_A += 1
        if i.allele_1 == 'a' and i.allele_2 == 'A':
            a_A += 1
        if i.allele_1 == 'A' and i.allele_2 == 'a':
            A_a += 1

    return (
        a_a,
        A_A,
        a_A,
        A_a,
    )


def to_purcent(a_a, A_A, a_A, A_a) -> (int, int, int):

    total = a_a + A_A + a_A + A_a

    if not total:
        return (0, 0, 0)

    return (
        round(a_a / total * 100),
        round(A_A / total * 100),
        round((a_A + A_a) / total * 100),
    )