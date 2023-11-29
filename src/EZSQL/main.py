# // ---------------------------------------------------------------------
# // ------- [EZSQL] EZSQL Main
# // ---------------------------------------------------------------------

# todo: "__WHERE" helper method for setting up the "WHERE" part of a SQL query
#       will be handy for future "remove" method, and will be handy to clean up "get" method 

# // ---- Imports
import os
import sqlite3
import pathlib

from . import helpers

# // ---- Variables
datatypes = {
    str : "TEXT",
    int : "INTEGER",
    float : "REAL"
}

# // ---- Classes
class EZSQL():
    # // setup
    def __init__(self, databasePath: str, timeout: float|int = 60):
        # set attributes
        self.folderPath = os.path.split(databasePath)[0]
        self.databasePath = databasePath
        self.tables = {}
        
        # make sure path exists
        pathlib.Path(self.folderPath).mkdir(
            parents = True,
            exist_ok = True
        )
        
        # create database
        self.database = sqlite3.connect(
            database = self.databasePath,
            timeout = timeout
        )
        
    # // helpers
    def __cursor(self):
        return self.database.cursor()
        
    def __execute(self, query: str, shouldCommit: bool = False, *params: str):
        print(query, params, sep = " | ")
        
        # get cursor
        cursor = self.__cursor()
        
        # execute query
        cursor.execute(query, params)
        
        # commit if desired
        if shouldCommit:
            self.database.commit()
        
        # return cursor
        return cursor
        
    def __getKeysAndValuesOfDict(self, inputDict: dict):
        return list(inputDict.keys()), list(inputDict.values())
    
    def __resultToValue(self, result: list, value: object) -> object:
        return value(*result)
    
    def __where(self, searchParams: object):
        # get attributes
        attributes, _ = helpers.listClassAttributes(searchParams)
        newSearchParams = {}
        
        # filter out search params (removing values that are none)
        for attributeName, attribute in attributes.items():
            if attribute is None:
                continue
            
            newSearchParams[attributeName] = attribute
        
        # construct sql query string (the "WHERE" part)
        values = []
        whereQueryPart = "" # "SELECT FROM _ WHERE {fromQueryPart}"
        count = 0
        
        for name, value in searchParams.items():
            if value is None:
                continue
            
            # increase count
            count += 1
            
            # add "and" after if this is not the last value
            andPart = " AND " if count < len(newSearchParams) else ""
            
            # create "x = y" part
            whereQueryPart += f"{name} = ?{andPart}"
            
            # append value to values list
            values.append(value)
            
        # return sql query and values
        return whereQueryPart, values
        
    # // main
    def createTable(self, tableName: str, table: object):
        # get columns of table
        columns, primaryColumn = helpers.listClassAttributes(table)
        queryColumns = ""
        
        # format columns into query string
        count = 0

        for name, value in columns.items():
            count += 1
            
            # get ending comma (only add if this is not the last value)
            endingComma = ", " if count < len(columns) else ""
            
            # set primary key if this is the primary column
            primaryKey = "PRIMARY KEY" if primaryColumn == name else ""
            
            # get data type
            columnType = datatypes[type(value)]

            # plop it all together and append to query
            queryColumns += f"{name} {columnType} {primaryKey}{endingComma}"
        
        # execute
        self.__execute(f"CREATE TABLE IF NOT EXISTS {tableName} ({queryColumns})")
        
    def removeTable(self, tableName: str):
        self.__execute(f"DROP TABLE {tableName}", True)
        
    def insert(self, tableName: str, obj: object):
        # get values
        objVars, _ = helpers.listClassAttributes(obj)
        names, values = self.__getKeysAndValuesOfDict(objVars)
        
        # format stuffs
        questionMarks = ", ".join(list("?" * len(objVars)))
        namesFormatted = ", ".join(names)
        
        # execute
        self.__execute(f"INSERT OR IGNORE INTO {tableName} ({namesFormatted}) VALUES ({questionMarks})", True, *values)

    def get(self, tableName: str, searchParameters: object, fetchHowMany: int = -1) -> list[object]|object:
        # get values
        objConstructor = type(searchParameters)

        # format search params into sql query
        whereQuery, values = self.__where(searchParameters)
            
        # execute
        result = self.__execute(f"SELECT * FROM {tableName} WHERE {whereQuery}", False, *values)
        
        # return result
        match fetchHowMany:
            # return all
            case -1:
                all = result.fetchall()
                return [self.__resultToValue(individual, objConstructor) for individual in all]
            
            # return one
            case 1:
                singular = result.fetchone()
                
                if result is None:
                    return
                
                return self.__resultToValue(singular, objConstructor)
            
            # return x
            case _:
                all = result.fetchmany(fetchHowMany)
                return [self.__resultToValue(individual, objConstructor) for individual in all]
            
    def remove(self, tableName: str, searchParameters: object):
        # format search params into sql query
        whereQuery, values = self.__where(searchParameters)
        
        # execute
        self.__execute(f"DELETE OR IGNORE FROM {tableName} WHERE {whereQuery}", True, *values)