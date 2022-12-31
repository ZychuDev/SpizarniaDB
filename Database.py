from neo4j import GraphDatabase
import logging
from neo4j.exceptions import ServiceUnavailable

class Database:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password), )

    def close(self):
        self.driver.close()

    @staticmethod
    def _create_and_return_recipe(tx, recipe_name, description):
        query = (
            """MATCH (p:Person)
                WHERE p.name = "Ja"
                CREATE (r:Recipe {name: $recipe_name, description: $description})
                CREATE (p)-[:WROTE]->(r)
                RETURN r"""     
        )
        result = tx.run(query, recipe_name=recipe_name, description=description)
        try:
            return [{"r": row["r"]["name"]} for row in result]
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    @staticmethod
    def _add_and_return_ingredient(tx, ingredient_name):
        query = (
        """MATCH 
            (p:Person),
            (i:Ingredient)
            WHERE p.name = "Ja" AND i.name = $ingredient_name
            CREATE (p)-[:HAS]->(i)
            RETURN i
        """
        )
        result = tx.run(query, ingredient_name=ingredient_name)
        try:
            return [{"i": row["i"]["name"]} for row in result]
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    @staticmethod
    def _get_ingredients(tx):
        query = (
            """MATCH (i:Ingredient)
                RETURN i
            """
        )
        result = tx.run(query)
        try:
            return [row["i"]["name"] for row in result]
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise
    
    @staticmethod
    def _get_my_ingredients(tx):
        query = (
            """MATCH (p:Person)-[:HAS]->(i:Ingredient)
                WHERE p.name = "Ja"
                RETURN i
            """
        )
        result = tx.run(query)
        try:
            return [row["i"]["name"] for row in result]
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    @staticmethod
    def _delete_ingredient(tx, name):
        query = (
            """OPTIONAL MATCH (p:Person {name: "Ja"})-[h:HAS]->(i:Ingredient {name: $name})
                DETACH DELETE h"""
        ) 
        tx.run(query, name=name)
     
    @staticmethod
    def _delete_recipe(tx, name):
        query = (
            """OPTIONAL MATCH (p:Person {name: "Ja"})-[w:WROTE]->(r:Recipe {name: $name})
                DETACH DELETE w
                DETACH DELETE r"""
        ) 
        tx.run(query, name=name)

    @staticmethod
    def _get_my_recipies(tx):
        query = (
            """MATCH (p:Person)-[:WROTE]->(r:Recipe)
                WHERE p.name = "Ja"
                RETURN r
            """
        )
        result = tx.run(query)
        try:
            return [row["r"] for row in result]
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    @staticmethod
    def _get_recipe(tx, name):
        query = (
            """MATCH (r:Recipe {name: $name})
            WITH r OPTIONAL MATCH (i:Ingredient)-[:IS_PART]->(r)
            WITH COUNT(i) as nr, r
            WITH r, nr MATCH (p:Person)-[:WROTE]->(r)
            RETURN r, nr, p
            """
        )
        result = tx.run(query, name=name)
        try:
            return [{"r": row["r"]["description"], "nr": row["nr"], "a": row["p"]} for row in result]
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
        raise   

    @staticmethod
    def _get_persons(tx):
        query = (
            """MATCH (p:Person)
                RETURN p    
            """
        )
        result = tx.run(query)
        try:
            return [row["p"]["name"] for row in result]
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))  

    @staticmethod
    def _get_followed(tx):
        query = (
            """MATCH (p:Person {name: "Ja"})-[:FOLLOW]->(p2:Person)
                RETURN p2  
            """
        )
        result = tx.run(query)
        try:
            return [row["p2"]["name"] for row in result]
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception)) 
    
    @staticmethod
    def _get_recipe_ingredients(tx, recipe_name):
        query = (
            """MATCH (r:Recipe {name: $recipe_name})-[:CONTAIN]->(i:Ingredient)
                RETURN i 
            """
        )
        result = tx.run(query, recipe_name = recipe_name)
        try:
            return [row["i"]["name"] for row in result]
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception)) 

    @staticmethod
    def _add_recipe_ingredient(tx, recipe_name, ingredient_name):
        query = (
        """MATCH 
            (r:Recipe),
            (i:Ingredient)
            WHERE r.name = $recipe_name AND i.name = $ingredient_name
            CREATE (r)-[:CONTAIN]->(i)
            CREATE (i)-[:IS_PART]->(r)
            RETURN i
        """
        )
        result = tx.run(query, recipe_name=recipe_name, ingredient_name=ingredient_name)
        try:
            return [row["i"]["name"] for row in result]
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))    

    @staticmethod
    def _remove_recipe_ingredient(tx, recipe_name, ingredient_name):
        query = (
            """OPTIONAL MATCH (r:Recipe {name: $recipe_name})-[c:CONTAIN]->(i:Ingredient {name: $ingredient_name})
                WITH c
                OPTIONAL MATCH (i:Ingredient {name: $ingredient_name})-[is:IS_PART]->(r2:Recipe {name: $recipe_name})
                DETACH DELETE c
                DETACH DELETE is"""
        )
        tx.run(query, recipe_name=recipe_name, ingredient_name=ingredient_name)

   
    @staticmethod
    def _follow(tx, name):
        query = (
        """MATCH 
            (p:Person),
            (p2:Person)
            WHERE p.name = "Ja" AND p2.name = $name
            CREATE (p)-[:FOLLOW]->(p2)
            RETURN p2
        """
        )
        result = tx.run(query, name=name)
        try:
            return [row["p2"]["name"] for row in result]
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    @staticmethod 
    def _unfollow(tx, name):
        query = (
        """OPTIONAL MATCH (p:Person {name: "Ja"})-[f:FOLLOW]->(p2:Person {name: $name})
            DETACH DELETE f
        """
        )
        tx.run(query, name=name)

    @staticmethod
    def _rank(tx):
        query = (
        """MATCH (i:Ingredient)<-[rel:CONTAIN]-(r:Recipe)
            RETURN i.name, count(rel) as recipes
            ORDER BY recipes DESC
        """ 
        )
        result = tx.run(query)
        try:
            return [(row["i.name"], row["recipes"]) for row in result]
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    @staticmethod
    def _analyze(tx, ingredients, allergens):
        query = (
        """MATCH (r:Recipe)

            WHERE all(i in $ingredients WHERE exists(
            (r)-[:CONTAIN]->(:Ingredient {name: i})))
            AND none(i in $allergens WHERE exists(
            (r)-[:CONTAIN]->(:Ingredient {name: i})))

            RETURN r.name AS recipe,
                [(r)-[:CONTAIN]->(i) | i.name]
                AS ingredients
            ORDER BY size(ingredients)
            LIMIT 20
        """ 
        )
        result = tx.run(query,ingredients=ingredients, allergens=allergens)
        try:
            return [row["recipe"] for row in result]
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def create_recipe(self, recipe_name, description):
        with self.driver.session() as session:
            result = session.write_transaction(
                self._create_and_return_recipe, recipe_name, description)
        return result

    def add_ingredient(self, ingredient_name):
        with self.driver.session() as session:
            result = session.write_transaction(self._add_and_return_ingredient, ingredient_name)
        return result

    def get_ingredients(self):
        with self.driver.session() as session:
            return session.read_transaction(self._get_ingredients)

    def get_my_ingredients(self):
        with self.driver.session() as session:
            return session.read_transaction(self._get_my_ingredients)

    def delete_ingredient(self, name):
        with self.driver.session() as session:
            return session.write_transaction(self._delete_ingredient, name)

    def get_my_recipies(self):
        with self.driver.session() as session:
            return session.read_transaction(self._get_my_recipies)

    def get_recipe(self, name):
        with self.driver.session() as session:
            return session.read_transaction(self._get_recipe, name)

    def get_persons(self):
        with self.driver.session() as session:
            return session.read_transaction(self._get_persons)

    def get_followed(self):
        with self.driver.session() as session:
            return session.read_transaction(self._get_followed)

    def get_recipe_ingredients(self, recipe_name):
        with self.driver.session() as session:
            return session.read_transaction(self._get_recipe_ingredients, recipe_name) 

    def add_recipe_ingredient(self, recipe_name, ingredient_name):  
        with self.driver.session() as session:
            return session.write_transaction(self._add_recipe_ingredient, recipe_name, ingredient_name)

    def remove_recipe_ingredient(self, recipe_name, ingredient_name):
        with self.driver.session() as session:
            return session.write_transaction(self._remove_recipe_ingredient, recipe_name, ingredient_name)

    def follow(self, name):
        with self.driver.session() as session:
            return session.write_transaction(self._follow, name)

    def unfollow(self, name):
        with self.driver.session() as session:
            return session.write_transaction(self._unfollow, name)

    def delete_recipe(self, name):
        with self.driver.session() as session:
            return session.write_transaction(self._delete_recipe, name)

    def rank(self):
        with self.driver.session() as session:
            return session.read_transaction(self._rank) 

    def analyze(self, ingredients, allergens):
        with self.driver.session() as session:
            return session.read_transaction(self._analyze, ingredients, allergens) 



    
