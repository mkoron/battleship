import random

#Create board and setup game

class Direction:
    HORIZONTAL = 0
    VERTICAL = 1

class Field:
    def __init__(self, row, column):
        self._row = row
        self._column = column
        self._free = True

    def __eq__(self, otherField):
        if type(otherField) is not type(self):
            return False
 
        return ((self._row == otherField._row) and (self._column == otherField._column))

    def __str__(self):
        return "Field({}, {})".format(self._row, self._column)

    def __hash__(self):
        return hash((self._row, self._column))

class Board:
    def __init__(self, rowNbr, columnNbr):
        self._rowNumber = rowNbr
        self._columnNumber = columnNbr
        self._fields = {(row, column): Field(row, column)
                        for row in range(self._rowNumber)
                        for column in range(self._columnNumber)}
            
    def _removeField(self, row, column):
        if (row, column) in self._fields:
            del(self._fields[row, column])

    def _getAvailableStartFields(self, shipSize):
        start = self._getFreeFields(shipSize, Direction.HORIZONTAL, lambda i,j: (i, j), (self._rowNumber, self._columnNumber))
        start.extend(self._getFreeFields(shipSize, Direction.VERTICAL, lambda i,j: (j, i), (self._columnNumber, self._rowNumber)))
        return start

    def _getFreeFields(self, size, direction, key, borders):
        start = []
        for i in range(borders[0]):
            freeFields = 0
            for j in range(borders[1]):
                if key(i, j) in self._fields:
                    freeFields += 1
                    if freeFields >= size:
                        end = j + 1 - size
                        pair = self._fields[key(i, end)], direction  
                        start.append(pair)
                else:
                    freeFields = 0
        return start

    def extractShipFields(self, startField, direction, size):
        fields = self._shipFields(startField, direction, size)
        self._removeAdjacentFields(fields)
      
        return fields

    def _shipFields(self, startField, direction, size):
        r0 = startField._row
        c0 = startField._column

        shipFields = []
        if direction == Direction.HORIZONTAL:
            for column in range(c0, c0 + size):
                shipFields.append(self._fields.pop((r0, column)))
        else:
            for row in range(r0, r0 + size):
                shipFields.append(self._fields.pop((row, c0)))

        return shipFields

    def _removeAdjacentFields(self, shipFields):
        upperRow = shipFields[0]._row - 1
        leftColumn = shipFields[0]._column - 1

        lowerRow = shipFields[-1]._row + 2
        rightColumn = shipFields[-1]._column + 2

        for row in range(upperRow, lowerRow):
            for column in range(leftColumn, rightColumn):
                self._removeField(row, column)

    def __str__(self):
        visual = "  "
        for column in range(self._columnNumber):
            visual = visual + chr(column  + ord('A'))

        for row in range(self._rowNumber):
            visual = "{}\n{:2}|".format(visual, row + 1)
            for column in range(self._columnNumber):
                if (row, column) in self._fields:
                    sign = ' '
                else:
                    sign = 'X'
                visual = visual + sign
            visual = visual + '|'
        return visual

class Ship:
    def __init__(self, fields):
        self._fields = fields
        self._hitFields = set()

    def shootField(self, row, column):
       
        for field in self._fields:
            print(self._hitFields)
            if field._row == row and field._column == column:
                self._hitFields.add(field)
            
                return (ShootingResults.SHIP_DESTROYED if self.isItDestroyed() 
                                                       else ShootingResults.HIT)

        return ShootingResults.MISS

    def isItDestroyed(self):
        return len(self._hitFields) == len(self._fields) 

class Shipbuilder:
    
    def getFleet(self, rowsNumber, columnsNumber, shipSizes):
        fleet = None
        
        while fleet == None:         
            board = Board(rowsNumber, columnsNumber)
            fleet = self._makeFleet(board, shipSizes)
        return fleet

    def _makeFleet(self, board, shipSizes):
        fleet = Fleet()
        for size in shipSizes:
            fields = self._putShip(board, size)
       
            if not fields:
                return None

            fleet.addShip(fields)

        return fleet

    def _putShip(self, board, size):
        startingFields = board._getAvailableStartFields(size)
        if len(startingFields) == 0:
            return None
        choosenField = self._getStartingField(startingFields)
        field = choosenField[0]
        direction = choosenField[1]
       
        return board.extractShipFields(field, direction, size)

    def _getStartingField(self, availableFields):
        return random.choice(availableFields)

class Fleet:

    def __init__(self):
        self._ships = []

    def addShip(self, fields):
        self._ships.append(Ship(fields))

    def shootField(self, row, column):
        for ship in self._ships:
            shootingResult = ship.shootField(row, column)
            print(shootingResult)
            if shootingResult == ShootingResults.HIT:
                return ShootingResults.HIT
            if shootingResult == ShootingResults.SHIP_DESTROYED:
                return (ShootingResults.FLEET_DESTROYED if self.allShipsDestroyed() 
                                                        else ShootingResults.SHIP_DESTROYED)
        return ShootingResults.MISS

    def allShipsDestroyed(self):
        nb = sum(1 for s in self._ships if s.isItDestroyed())
        return nb == len(self._ships)

    def __str__(self):
        rowsNumber = 0
        columnsNumber = 0
        for ship in self._ships:
            for field in ship._fields:
                if field._row > rowsNumber:
                    rowsNumber = field._row
                if field._column > columnsNumber:
                    columnsNumber = field._column

        b = Board(rowsNumber + 1, columnsNumber + 1)
        for ship in self._ships:
            for field in ship._fields:
                b._removeField(field._row, field._column)

        return b.__str__()

# Game logic

class ShootingResults:
    MISS = 0
    HIT = 1
    SHIP_DESTROYED = 2
    FLEET_DESTROYED = 3

class FieldState:
    AVAILABLE = 0
    ELIMINATED = 1
    MISS = 2
    HIT = 3
    SHIP_DESTROYED = 4

class HitField:
    def __init__(self, row, column):
        self._row = row
        self._column = column
        self._fieldState = FieldState.AVAILABLE

    def recordResult(self, result):
        self._fieldState = result

    def isItAvailable(self):
        return self._fieldState == FieldState.AVAILABLE

class HitBoard:

    def __init__(self, rowsNbr, columnsNbr):
        self._rowsNumber = rowsNbr
        self._columnsNumber = columnsNbr

        self._fields = {(r, c):HitField(r, c) for r in range(_rowsNumber) for c in range(_columnsNumber)}

    def getShipFields(self, shipSize):
        fields = self._fieldsForHorizontalShip(shipSize)
        fields.extend(self._fieldsForVerticalShIps(shipSize))
        return fields

    def _fieldsForHorizontalShip(self, shipSize):
        return self._shipFields(shipSize, lambda i, j:  self._fields[i, j], self._rowsNumber, self._columnsNumber)

    def _fieldsForVerticalShIps(self, shipSize):
        return self._shipFields(shipSize, lambda i, j:  self._fields[j, i], self._columnsNumber, self._rowsNumber)

    def _shipFields(self, size, getField, imax, jmax):
        fields = []
        for i in range(imax):
            places = 0
            for j in range(jmax):
                if getField(i, j).isItAvailable():
                    places += 1

                    if places >= size:
                        for jj in range(j - size + 1, j + 1):
                            fields.append(getField(i, jj))
                else:
                    places = 0
        return fields
    
    def markDestroyed(self, fields):
        for field in fields:
            field.recordResult(FieldState.SHIP_DESTROYED)
            self._removeOtherFields(fields)

    def _removeOtherFields(self, fields):
        pass

class Artillery:
    def __init__(self, rowsNbr, colsNbr, shipSizes):
        self._grid = HitBoard(rowsNbr, colsNbr)
        self._shipSizes = list(shipSizes)
        self._shootField = None
        self._fieldsShootShip = []

    def shoot(self):
        pass

    def processResults(self, shootingResults):
        self._grid.recordShooting(self._shootField, shootingResults)

        if shootingResults == ShootingResults.MISS:
            return False

        self._fieldsShootShip.append(self._shootField)
        self._fieldsShootShip.sort(key=lambda field: field._row + field._column)

        if shootingResults == ShootingResults.FLEET_DESTROYED:
            self._grid.markDestroyed(self._fieldsShootShip)
            return True

        if shootingResults == ShootingResults.SHIP_DESTROYED:
            self._grid.markDestroyed(self._fieldsShootShip)
            shipSize = len(self._fieldsShootShip)
            self._shipSizes.remove(shipSize)
            self._fieldsShootShip.clear()

            if len(self._shipSizes) == 0:
                return True

        return False


ispisi = {ShootingResults.MISS: "Miss",
        ShootingResults.HIT: "Hit",
        ShootingResults.SHIP_DESTROYED: "Ship destroyed",
        ShootingResults.FLEET_DESTROYED: "Fleet destroyed!!!"}

ships = [5, 4, 4, 3, 3, 3, 2, 2, 2, 2]

fleet = Shipbuilder()._makeFleet(Board(10, 10), ships)

print("Enter the field that you want to hit (row-column)")

fleetDestroyed = False
nbTries = 0
print(fleet)

while fleetDestroyed == False:
    nbTries += 1
    unos = input("Next field: ").lower().split('-')
    row = int(unos[1]) - 1
    column = ord(unos[0]) - ord('a')
    result = fleet.shootField(row, column)
    print(ispisi[result])
    if (result == ShootingResults.FLEET_DESTROYED):
        fleetDestroyed = True

print("After {0} tries".format(nbTries))
