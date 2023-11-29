# // ---------------------------------------------------------------------
# // ------- [EZSQL] EZSQL Main
# // ---------------------------------------------------------------------

# // ---- Imports
import os
import sqlite3
import pathlib
import typing

from . import helpers

# // ---- Variables
class dataTypes():
    stringType = "TEXT"
    integerType = "INTEGER"
    floatType = "REAL"

# // ---- Classes
# // Table Class
class table():
    # // setup
    def __init__(self, name: str, columns: list["table"], valueObj: object, parent: "EZSQL"):
        self.name = name
        self.columns = columns
        self.valueObject = valueObj
        self.parent = parent
        
    # // methods
    def insert(self, value: object):
        return self.parent.insert(self, value)
    
    def get(self, searchParameters: object, fetchAmount: int = -1):
        return self.parent.get(self, searchParameters, fetchAmount)
    
    def getAll(self):
        return self.parent.getAll(self)
    
    def removeTable(self):
        return self.parent.removeTable(self)
    
    def remove(self, searchParameters: object):
        return self.parent.remove(self, searchParameters)
    
    def removeAll(self):
        return self.parent.removeAll(self)
    
    # // magic methods
    def __del__(self):
        return self.removeTable()

# // Column Class
class column():
    # // setup
    def __init__(self, type: str, default: typing.Any, isPrimary: bool = False):
        self.type = type
        self.default = default
        self.isPrimary = isPrimary

# // Main EZSQL Class
# Represented as "database" in the package __init__
class EZSQL():
    # // setup
    def __init__(self, databasePath: str, timeout: float|int = 60):
        # set attributes
        self.folderPath = os.path.split(databasePath)[0]
        self.databasePath = databasePath
        self.tables: dict[str, "table"] = {}
        
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
    
    def __resultToValue(self, result: list, table: "table") -> object:
        return table.valueObject(*result)
    
    def __where(self, searchParams: object) -> tuple[str, list[str]]:
        # get attributes
        attributes = helpers.listClassAttributes(searchParams)
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
        
        for name, value in newSearchParams.items():
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
    def createTable(self, tableName: str, tableObj: object) -> "table":
        # get columns of table
        columns: dict[str, "column"] = helpers.listClassAttributes(tableObj)
        queryColumns = ""
        
        # format columns into query string
        count = 0

        for name, value in columns.items():
            count += 1
            
            # get ending comma (only add if this is not the last value)
            endingComma = ", " if count < len(columns) else ""
            
            # set primary key if this is the primary column
            primaryKey = "PRIMARY KEY" if value.isPrimary else ""
            
            # plop it all together and append to query
            queryColumns += f"{name} {value.type} {primaryKey}{endingComma}"
            
        # register table
        createdTable = table(
            name = tableName,
            columns = list(columns.values()),
            valueObj = tableObj
        )

        self.tables[tableName] = createdTable
        
        # execute
        self.__execute(f"CREATE TABLE IF NOT EXISTS {tableName} ({queryColumns})")
        
        # return
        return createdTable
        
    def getTable(self, name: str) -> "table":
        return self.tables.get(name, None)
        
    def removeTable(self, table: "table"):
        self.__execute(f"DROP TABLE {table.name}", True)
        self.tables.pop(table.name, None)
        
    def insert(self, table: "table", value: object):
        # get values
        objVars = helpers.listClassAttributes(value)
        names, values = self.__getKeysAndValuesOfDict(objVars)
        
        # format stuffs
        questionMarks = ", ".join(list("?" * len(objVars)))
        namesFormatted = ", ".join(names)
        
        # execute
        self.__execute(f"INSERT OR IGNORE INTO {table.name} ({namesFormatted}) VALUES ({questionMarks})", True, *values)

    def get(self, table: "table", searchParameters: object, fetchAmount: int = -1) -> list[object]|object:
        # format search params into sql query
        whereQuery, values = self.__where(searchParameters)
            
        # execute
        result = self.__execute(f"SELECT * FROM {table.name} WHERE {whereQuery}", False, *values)
        
        # return result
        match fetchAmount:
            # return all
            case -1:
                all = result.fetchall()
                return [self.__resultToValue(individual, table) for individual in all]
            
            # return one
            case 1:
                singular = result.fetchone()
                
                if result is None:
                    return
                
                return self.__resultToValue(singular, table)
            
            # return x
            case _:
                all = result.fetchmany(fetchAmount)
                return [self.__resultToValue(individual, table) for individual in all]
            
    def getAll(self, table: "table"):
        all = self.__execute(f"SELECT * FROM {table.name}").fetchall()
        return [self.__resultToValue(individual, table) for individual in all]
            
    def remove(self, table: "table", searchParameters: object):
        # format search params into sql query
        whereQuery, values = self.__where(searchParameters)
        
        # execute
        self.__execute(f"DELETE FROM {table.name} WHERE {whereQuery}", True, *values)
        
    def removeAll(self, table: "table"):
        # execute
        self.__execute(f"DELETE FROM {table.name}", True)