from motif_analyzer import mongo

from bson import ObjectId
from datetime import datetime


class Sequence(object):
    """
    Sequence document object model
    """

    @staticmethod
    def insert_one(collection_id=None, sequence_id=None, sequence_name=None, sequence_description=None, sequence=None,
                   user=None):
        """
        Creates a document and inserts it into MongoDB collection
        :param collection_id:
        :param sequence_id:
        :param sequence_name:
        :param sequence_description:
        :param sequence:
        :param user:
        :return ObjectId:
        """
        if collection_id and sequence_id and sequence_name and sequence_description and sequence and user\
            and isinstance(collection_id, ObjectId) and isinstance(sequence_id, str) and isinstance(sequence_name, str)\
            and isinstance(sequence_description, str) and isinstance(sequence, str) and isinstance(user, str)\
            and len(sequence_id) > 0 and len(sequence_name) > 0 and len(sequence_description) > 0 \
                and len(sequence) > 0 and len(user) > 0:
            document = {
                'collection_id': ObjectId(collection_id),
                'sequence_id': sequence_id,
                'sequence_name': sequence_name,
                'sequence_description': sequence_description,
                'sequence': sequence,
                'datetime_added': datetime.utcnow(),
                'user': user,
            }
            return mongo.db.sequence.insert_one(document).inserted_id
        
        return None

    @staticmethod
    def find_one(document_id=None):
        """
        Queries MongoDB for single document via ObjectId pk
        :param document_id:
        :return dict:
        """
        if document_id and isinstance(document_id, ObjectId):
            return mongo.db.sequence.find_one({'_id': document_id})
        
        return None

    @staticmethod
    def find(collection_id=None, user=None):
        """
        Queries MongoDB for one or more documents via attribute match
        :param collection_id:
        :param user:
        :return iterator:
        """
        if collection_id and isinstance(collection_id, ObjectId) and not user:
            return mongo.db.sequence.find({'collection_id': collection_id})

        elif user and isinstance(user, str) and not collection_id:
            return mongo.db.sequence.find({'user': user})

        elif collection_id and user and isinstance(collection_id, ObjectId) and isinstance(user, str):
            return mongo.db.sequence.find({'$and': [{'collection_id': collection_id}, {'user': user}]})
        
        return None

    @staticmethod
    def delete_one(document_id=None):
        """
        Deletes one MongoDB document from collection via ObjectId pk
        :param document_id:
        :return integer:
        """
        if document_id and isinstance(document_id, ObjectId):
            return mongo.db.sequence.delete_one({'_id': document_id}).deleted_count
        
        return None

    @staticmethod
    def delete_many(collection_id=None):
        """
        Deletes one or more MongoDB documents from collection via attribute match
        :param collection_id:
        :return integer:
        """
        if collection_id and isinstance(collection_id, ObjectId):
            return mongo.db.sequence.delete_many({'query_id': collection_id}).deleted_count
        
        return None


class Motif(object):
    """
    Motif document object model
    """

    @staticmethod
    def insert_one(motif=None, user=None):
        """
        Creates a document and inserts it into MongoDB collection
        :param motif:
        :param user:
        :return bson.ObjectId:
        """
        if motif and user and isinstance(motif, str) and isinstance(user, str) and len(motif) > 0 and len(user) > 0:
            document = {
                'motif': motif,
                'datetime_added': datetime.utcnow(),
                'user': user,
            }
            return mongo.db.motif.insert_one(document).inserted_id
        
        return None

    @staticmethod
    def find_one(document_id=None):
        """
        Queries MongoDB for single document via ObjectId pk
        :param document_id:
        :return dict:
        """
        if document_id and isinstance(document_id, ObjectId):
            return mongo.db.motif.find_one({'_id': document_id})
        
        return None

    @staticmethod
    def find(motif=None, user=None):
        """
        Queries MongoDB for one or more documents via attribute match
        :param motif:
        :param user:
        :return iterator:
        """
        if motif and isinstance(motif, str) and not user:
            return mongo.db.motif.find({'motif': motif})
        
        elif user and isinstance(user, str) and not motif:
            return mongo.db.motif.find({'user': user})
        
        elif motif and isinstance(motif, str) and user and isinstance(user, str):
            return mongo.db.motif.find({'$and': [{'motif': motif}, {'user': user}]})
        
        return None

    @staticmethod
    def delete_one(document_id=None):
        """
        Deletes one MongoDB document from collection via ObjectId pk
        :param document_id:
        :return integer:
        """
        if document_id and isinstance(document_id, ObjectId):
            return mongo.db.motif.delete_one({'_id': document_id}).deleted_count
        
        return None


class Query(object):
    """
    Query document object model
    """

    @staticmethod
    def insert_one(motif_id_list=None, collection_id_list=None, motif_frequency=None, motif_frame_size=None, user=None):
        """
        Creates a document and inserts it into MongoDB collection
        :param motif_id_list:
        :param collection_id_list:
        :param motif_frequency:
        :param motif_frame_size:
        :param user:
        :return:
        """
        if motif_id_list and collection_id_list and motif_frequency and motif_frame_size and user\
                and isinstance(motif_id_list, list) and isinstance(collection_id_list, list)\
                and isinstance(motif_frequency, int) and isinstance(motif_frame_size, int) and isinstance(user, str)\
                and len(motif_id_list) > 0 and len(collection_id_list) > 0 and 1 < motif_frequency < 11\
                and 9 < motif_frame_size < 1001 and len(user) > 0:
            document = {
                'motif_id_list': motif_id_list,
                'collection_id_list': collection_id_list,
                'motif_frequency': motif_frequency,
                'motif_frame_size': motif_frame_size,
                'datetime_added': datetime.utcnow(),
                'user': user,
            }
            return mongo.db.query.insert_one(document).inserted_id
        
        return None

    @staticmethod
    def find_one(document_id=None):
        """
        Queries MongoDB for single document via ObjectId pk
        :param document_id:
        :return dict:
        """
        if document_id and isinstance(document_id, ObjectId):
            return mongo.db.query.find_one({'_id': document_id})
        return None

    @staticmethod
    def delete_one(document_id=None):
        """
        Deletes one MongoDB document from collection via ObjectId pk
        :param document_id:
        :return integer:
        """
        if document_id and isinstance(document_id, ObjectId):
            return mongo.db.query.delete_one({'_id': document_id}).deleted_count
        
        return None


class Collection(object):
    """
    Collection document object model
    """

    @staticmethod
    def insert_one(collection_name=None, collection_type=None, user=None):
        """
        Creates a document and inserts it into MongoDB collection
        :param collection_name:
        :param collection_type:
        :param user:
        :return ObjectId:
        """
        if collection_name and collection_type and user and isinstance(collection_name, str)\
                and isinstance(collection_type, str) and isinstance(user, str):
            document = {
                'collection_name': collection_name,
                'collection_type': collection_type,
                'datetime_added': datetime.utcnow(),
                'user': user,
            }
            return mongo.db.collection.insert_one(document).inserted_id

        return None

    @staticmethod
    def find_one(document_id=None):
        """
        Queries MongoDB for single document via ObjectId pk
        :param document_id:
        :return dict:
        """
        if document_id and isinstance(document_id, ObjectId):
            return mongo.db.collection.find_one({'_id': document_id})

        return None

    @staticmethod
    def find(user=None):
        """
        Queries MongoDB for one or more documents via attribute match
        :param user:
        :return iterator:
        """
        if user and isinstance(user, str):
            return mongo.db.collection.find({'user': user})

        return None

    @staticmethod
    def delete_one(document_id=None):
        """
        Deletes one MongoDB document from collection via ObjectId pk
        :param document_id:
        :return integer:
        """
        if document_id and isinstance(document_id, ObjectId):
            return mongo.db.collection.delete_one({'_id': document_id}).deleted_count

        return None

    @staticmethod
    def delete_many(user=None):
        """
        Deletes one or more MongoDB documents from collection via attribute match
        :param user:
        :return integer:
        """
        if user and isinstance(user, str):
            return mongo.db.collection.delete_many({'user': user}).deleted_count

        return None


class Result(object):
    """
    Result document object model
    """

    @staticmethod
    def insert_one(query_id=None, sequence_description=None, sequence=None, analysis=None, has_motif=None, user=None):
        """
        Creates a document and inserts it into MongoDB collection
        :param query_id:
        :param sequence_description:
        :param sequence:
        :param analysis:
        :param has_motif:
        :param user:
        :return ObjectId:
        """
        if query_id and sequence_description and sequence and analysis and has_motif and user\
                and isinstance(query_id, ObjectId) and isinstance(sequence_description, str)\
                and isinstance(sequence, str) and isinstance(analysis, list) and isinstance(has_motif, bool)\
                and isinstance(user, str):
            document = {
                'query_id': query_id,
                'sequence_description': sequence_description,
                'sequence': sequence,
                'analysis': analysis,
                'has_motif': has_motif,
                'datetime_added': datetime.utcnow(),
                'user': user,
            }
            return mongo.db.result.insert_one(document).inserted_id

        return None

    @staticmethod
    def find_one(document_id=None):
        """
        Queries MongoDB for single document via ObjectId pk
        :param document_id:
        :return dict:
        """
        if document_id and isinstance(document_id, ObjectId):
            return mongo.db.result.find_one({'_id': document_id})

        return None

    @staticmethod
    def find(query_id=None, user=None):
        """
        Queries MongoDB for one or more documents via attribute match
        :param query_id:
        :param user:
        :return iterator:
        """
        if query_id and isinstance(query_id, ObjectId) and not user:
            return mongo.db.result.find({'collection_id': query_id})
        elif user and isinstance(user, str) and not query_id:
            return mongo.db.result.find({'user': user})
        elif query_id and user and isinstance(query_id, ObjectId) and isinstance(user, str):
            return mongo.db.result.find({'$and': [{'query_id': query_id}, {'user': user}]})

        return None

    @staticmethod
    def delete_one(document_id=None):
        """
        Deletes one MongoDB document from collection via ObjectId pk
        :param document_id:
        :return integer:
        """
        if document_id and isinstance(document_id, ObjectId):
            return mongo.db.result.delete_one({'_id': document_id}).deleted_count

        return None

    @staticmethod
    def delete_many(query_id=None, user=None):
        """
        Deletes one or more MongoDB documents from collection via attribute match
        :param query_id:
        :param user:
        :return integer:
        """
        if query_id and isinstance(query_id, ObjectId) and not user:
            return mongo.db.result.delete_many({'collection_id': query_id})
        elif user and isinstance(user, str) and not query_id:
            return mongo.db.result.delete_many({'user': user})
        elif query_id and user and isinstance(query_id, ObjectId) and isinstance(user, str):
            return mongo.db.result.delete_many({'$and': [{'query_id': query_id}, {'user': user}]})

        return None
