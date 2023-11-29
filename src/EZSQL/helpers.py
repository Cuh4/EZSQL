# // ---------------------------------------------------------------------
# // ------- [EZSQL] EZSQL Helpers
# // ---------------------------------------------------------------------

# // ---- Functions
def listClassAttributes(target: object) -> tuple[dict[str, any], str]:
    # define exceptions
    exceptions = ["__module__", "__dict__", "__weakref__", "__doc__"]
    typeExceptions = ["function"]
    
    # set vars for later
    attributes = {}
    primary = None
    
    # get all class attributes
    for varName, var in vars(target).items():
        # exceptions check
        if varName in exceptions or type(var).__name__ in typeExceptions:
            continue
        
        # set primary if this is the first attribute
        if primary is None:
            primary = varName
            
        # save attribute
        attributes[varName] = var
            
    # return
    return attributes, primary