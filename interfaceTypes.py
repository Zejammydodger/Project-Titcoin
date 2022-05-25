
"""
ok heres the idea:
    this will be essentially a header file in a C program, it will contain definitions for types such as 
    Person or Company each with all of their *essential* functions defined to raise notimplemented by defualt
    
    the reason for doing this is so that any new version of sqlhelper for example can just override the essential
    functions (while defineing new ones if need be) and the main titcoin file will just work based off the 
    assumtion that all of these types are the interface types, meaning they will always work (or raise notImplemented)
    
    tl;dr:
    define the types here so that we dont have to re write the implementation every time we change how it works 

"""