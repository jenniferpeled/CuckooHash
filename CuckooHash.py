import time
import random
import pytest
from BitHash import *
import cityhash
import string

class Node(object):
    def __init__(self, k, d):
        self.k  = k
        self.d = d


class CuckooHash(object):
    def __init__(self, size):
        self.__firstArray = [None] * size
        self.__secondArray = [None] * size
        self.__firstKeys = 0
        self.__secondKeys = 0
        self.__size = size
    
    
    
    def __insert(self, k, d, first = '', second = ''): 
        if first == '': first = self.__firstArray                               # Set default params to make growHash simpler. 
        if second == '': second = self.__secondArray 
   
        temp = Node(k,d)  
        currentHash = None
        attempts = 0
        
        while attempts < 50: 
        
            if attempts % 2 == 0:                                               # Switches between hash tables each attempt, 
                currentHash = first                                             # since the current temp will always replace the old.
                num = 1
            else: 
                currentHash = second 
                num = 2
            
            position = BitHash(temp.k, num) % len(currentHash)                  
            if not currentHash[position]:                                   
                currentHash[position] = temp                                
                if attempts % 2 == 0:
                    self.__firstKeys += 1
                else:
                    self.__secondKeys += 1
                return True
            
            elif currentHash[position].k == temp.k:
                raise Exception("Duplicates are not permitted.")
            
            else:                                                               # If there is a collision, swap the current temp and whatever was in that position,
                currentHash[position], temp = temp, currentHash[position]       # so the old Node is cuckoo'd out and becomes the new item attempted to insert.
                
            attempts += 1 
        
        for i in range(3):
            if self.__growAndReset(temp):                                       # If it still has not yet worked, grow the hash and reset the seed,
                return True                                                     # up to three times. 
            
        raise Exception("This insert is nonfunctional")
    
    
    
    def insert(self,k,d):                                                       # Public insert method for the client.
        if self.__secondKeys > self.__size*0.5 or \
           self.__firstKeys > self.__size*0.5:
            self.__growHash()   
        self.__insert(k,d)
       
       
    
    def __growHash(self):                                                       # Function used when tables become too full.
        newFirst = [None] * (self.__size * 2)
        newSecond = [None] * (self.__size * 2)
        self.__size = self.__size * 2 
        self.__secondKeys = 0
        self.__firstKeys = 0
        for i in self.__firstArray:
            if i: self.__insert(i.k, i.d, newFirst, newSecond)                        
        for i in self.__secondArray:
            if i: self.__insert(i.k, i.d, newFirst, newSecond)  
        self.__firstArray = newFirst                                        
        self.__secondArray = newSecond    
      

    
    def __growAndReset(self,temp):                                              # Function used when regular insert fails.
        ResetBitHash()                                                              
        self.__growHash()                                                       # Reset seed, make tables bigger, try again to insert.
        check = self.__insert(temp.k,temp.d)                                     
        if check: return True
        else: return False
    
    
    
    def find(self,k):        
        position = BitHash(k,1) % len(self.__firstArray)                        # Search the first table, return data if found.
        if self.__firstArray[position] and self.__firstArray[position].k == k: 
            return self.__firstArray[position].d                                        
        else:
            position = BitHash(k,2) % len(self.__secondArray)                   # Otherwise, check the second table and return data if found.           
            if self.__secondArray[position] and self.__secondArray[position].k == k:  
                return self.__secondArray[position].d                                        
            else:       
                return None
    
    
    
    def delete(self,k):
        position = BitHash(k,1) % len(self.__firstArray)                        # Search the first table, and delete the Node if found.
        if self.__firstArray[position] and self.__firstArray[position].k == k:                                 
            deleted = self.__firstArray[position] 
            self.__firstArray[position] = None 
            self.__firstKeys -= 1                                                
            return deleted.d
        else:
            position = BitHash(k,2) % len(self.__secondArray)                   # Otherwise, search the second table, and delete the Node if found.
            if self.__secondArray[position] and self.__secondArray[position].k == k:                             
                deleted = self.__secondArray[position]
                self.__secondArray[position] = None
                self.__secondKeys -= 1       
                return deleted.d
            else:
                return None                                                     # If the delete failed because the key was not there, return None.    
    
    
    
    def printOut(self):                                                         # Printing method used for my own tests.
        print("FIRST TABLE: ")
        for i in self.__firstArray:
            if i: print(i.k + " ",end="")
        print()
        print("SECOND TABLE: ")
        for i in self.__secondArray:
            if i: print(i.k + " ",end="")
            
    
    def testingInsert(self):                                                    # Returns a list of all keys successfully inserted
        keys = [ ]
        for i in self.__firstArray:
            if i: keys.append(i.k)
        for d in self.__secondArray:
            if d: keys.append(d.k)
        return keys
        
            
        

###############
### TESTING ###
###############

def test_smallFind():
    c = CuckooHash(5)
    c.insert("APPLE",3)
    c.insert("BANANA",2)
    c.insert("GRAPES",1)
    assert c.find("APPLE") == 3
    
def test_notThereSmallFind():
    c = CuckooHash(5)
    c.insert("APPLE",3)
    c.insert("BANANA",2)
    c.insert("GRAPES",1)
    assert c.find("MELON") == None

def test_oneFind():
    c = CuckooHash(1)
    c.insert("APPLE",3)
    c.insert("BANANA",2)
    c.insert("GRAPES",1)
    assert c.find("APPLE") == 3

def test_smallDelete():
    c = CuckooHash(5)
    c.insert("APPLE",3)
    c.insert("BANANA",2)
    c.insert("GRAPES",1)
    assert c.delete("GRAPES") == 1
    
def test_notThereSmallDelete():
    c = CuckooHash(3)
    c.insert("APPLE",3)
    c.insert("BANANA",2)
    c.insert("GRAPES",1)
    assert c.delete("JENNIE") == None
    
def test_oneDelete():
    c = CuckooHash(1)
    c.insert("APPLE",3)
    c.insert("BANANA",2)
    c.insert("GRAPES",1)
    assert c.delete("APPLE") == 3        

def test_smallInsert():
    c = CuckooHash(5)
    c.insert("APPLE",3)
    c.insert("BANANA",2)
    c.insert("GRAPES",1)
    keys = c.testingInsert()
    assert "APPLE" in keys
    assert "BANANA" in keys
    assert "GRAPES" in keys

def test_tooSmallInsert():
    c = CuckooHash(2)
    c.insert("APPLE",3)
    c.insert("BANANA",2)
    c.insert("GRAPES",1)
    c.insert("PEAR",4)
    c.insert("LEMON",5)
    keys = c.testingInsert()
    assert "APPLE" in keys
    assert "BANANA" in keys
    assert "GRAPES" in keys
    assert "PEAR" in keys
    assert "LEMON" in keys

def test_randomizedInsert():
    c = CuckooHash(1)
    d = [ ]
    for i in range(100):
        word = ''.join(random.choices(string.ascii_lowercase, k=5))
        c.insert(word,1)
        d.append(word)
    for words in d:
        if not c.find(words): assert False
    assert True
    



pytest.main(["-v", "-s", "CuckooHash.py"])