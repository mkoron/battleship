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
        visual = "   "
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

class ShootingFase:
    RANDOM = 0
    AFTER_FIRST_HIT = 1
    DESROY_SHIP = 2

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

        self._fields = {(r, c):HitField(r, c) for r in range(self._rowsNumber) for c in range(self._columnsNumber)}

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
    
    def recordShot(self, field, shootingResult):
        if shootingResult == ShootingResults.MISS:
            field.recordResult(FieldState.MISS)
            return

        if shootingResult == shootingResult.HIT:
            field.recordResult(FieldState.HIT)
            self._removeDiagonalFields(field)

    def _removeDiagonalFields(self, field):
        row = field._row
        column = field._column
        keys = [(row - 1, column - 1),
                (row - 1, column + 1)
                (row + 1, column - 1)
                (row + 1, column + 1)]

        for key in keys:
            self._removeField(key)

    def _removeField(self, key):
        if key in self._fields:
            field = self._fields[key]
            field.recordResult(FieldState.ELIMINATED)

    def markDestroyed(self, fields):
        for field in fields:
            field.recordResult(FieldState.SHIP_DESTROYED)
            self._removeOtherFields(fields)

    def _removeOtherFields(self, fields):
        print(fields[0])
        if fields[0]._column == fields[-1]._column:
            column = fields[0]._column
            self._removeField((fields[0]._row - 1, column))
            self._removeField((fields[-1]._row + 1, column))

        if fields[0]._row == fields[-1]._row:
            row = fields[0]._row
            self._removeField((row, fields[0]._column - 1))
            self._removeField((row, fields[-1]._column + 1,))      

    def fieldsSameDirection(self, field, direction):
        row = field._row
        column = field._column

        if direction == FieldDirection.LEFT:
            span = range(column - 1, -1,  -1) 
        elif direction == FieldDirection.RIGHT:
            span = range(column + 1, self._columnsNumber)
        elif direction == FieldDirection.UP:
            span = range(row - 1, -1,  -1)
        else:
            span = range(row + 1, self._rowsNumber)

        fields = []

        if direction == FieldDirection.LEFT or direction == FieldDirection.RIGHT:
            for c in span:
                if self._field[row, c].isItAvailable():
                    fields.append(self._fields[row, c])
                else:
                    break
        else:
            for r in span:
                if self._field[r, column].isItAvailable():
                    fields.append(self._fields[r, column])
                else:
                    break     

        return fields

class Artillery:
    def __init__(self, rowsNbr, colsNbr, shipSizes):
        self._grid = HitBoard(rowsNbr, colsNbr)
        self._shipSizes = list(shipSizes)
        self._f1 = ShootingFase.RANDOM
        self._f2 = ShootingFase.AFTER_FIRST_HIT
        self._f3 = ShootingFase.DESROY_SHIP
        self._tacticts = {
                           self._f1: RandomChooseField,
                           self._f2: ChooseFieldAfterFirstHit,
                           self._f3: ChooseFieldSystematicShooting}
        self._startRandomShooting()
        self._shootField = None
        self._fieldsShootShip = []

    def shoot(self):
        self._shootField = self._shootingTactict.chooseField()
        return self._shootField

    def processResults(self, shootingResults):
    
        if shootingResults == ShootingResults.MISS:
            self._grid.recordShot(self._shootField, shootingResults)
            return False

        self._fieldsShootShip.append(self._shootField)
        self._fieldsShootShip.sort(key=lambda field: field._row + field._column)

        self._grid._removeField(self._shootField)

        if shootingResults == ShootingResults.SHIP_DESTROYED:
            shipSize = len(self._fieldsShootShip)
            print(self._shipSizes)
            self._shipSizes.remove(shipSize)
            self._fieldsShootShip.clear()

            if len(self._shipSizes) == 0:
                return True
            self._startRandomShooting()
        return False

    def _startRandomShooting(self):
        self._shootingFase = ShootingFase.RANDOM
        self._shootingTactict = self._tacticts[self._shootingFase] \
            (self._grid, self._getLongestShipForShooting())

    def _startShootingFieldAfterFirstHit(self):
        self._shootingFase = ShootingFase.AFTER_FIRST_HIT
        self._shootingTactict = self._tacticts[self._shootingFase] \
            (self._grid, self._shootField)

    def _startSystematicShooting(self):
        self._shootingFase = ShootingFase.SHIP_DESTROYED
        self._shootingTactict = self._tacticts[self._shootingFase] \
            (self._grid, self._fieldsShootShip)

    def _getLongestShipForShooting(self):
        return max(self._shipSizes)

    def addNewTactic(self, shootingFase, shootingTactict):
        self._tacticts[shootingFase] = shootingTactict

class RandomChooseField:
    
    def __init__(self, grid, shipSize):
        self._grid = grid
        self._shipSize = shipSize

    def chooseField(self):
        fields = self._grid.getShipFields(self._shipSize)
        return random.choice(fields)

class FieldDirection:
    LEFT = 0
    UP = 1
    RIGHT = 2
    DOWN = 3

class ChooseFieldAfterFirstHit:
    def __init__(self, grid, hitField):
        self._grid = grid
        self._hitField = hitField

    def chooseField(self):
        nearbyFields = [self._grid.fieldsSameDirection(self._hitField, FieldDirection.LEFT),
                        self._grid.fieldsSameDirection(self._hitField, FieldDirection.UP),
                        self._grid.fieldsSameDirection(self._hitField, FieldDirection.RIGHT),
                        self._grid.fieldsSameDirection(self._hitField, FieldDirection.DOWN)]

        longestDirection = max(nearbyFields, key=lambda i: len(i))

        return longestDirection[0]

class ChooseFieldSystematicShooting:
    
    def __init__(self, grid, shipsHit):
        self._grid = grid
        self._fieldsShotShip = shipsHit

    def chooseField(self):
        firstField = self._fieldsShotShip[0]
        lastField = self._fieldsShotShip[-1]

        if firstField._row == lastField._row:
            nearby = [self._grid.fieldsSameDirection(firstField, FieldDirection.LEFT),
                      self._grid.fieldsSameDirection(lastField, FieldDirection.RIGHT)]
        else:
            nearby = [self._grid.fieldsSameDirection(firstField, FieldDirection.UP),
                      self._grid.fieldsSameDirection(firstField, FieldDirection.DOWN)]

        longestDirection = max(nearby, key=lambda i: len(i))

        return longestDirection[0]

def EnterScore():
    while True:
        result = input("(M)issed, (H)it or (S)inking:")

        if result.lower() == 'm':
            return ShootingResults.MISS
        elif result.lower() == 'h':
            return ShootingResults.HIT
        elif result.lower() == 's':
            return ShootingResults.SHIP_DESTROYED
        print("Invalid input!")

ships = [5, 4, 4, 3, 3, 3, 2, 2, 2, 2]



print("Enter the field that you want to hit (row-column)")

fleetDestroyed = False
nbTries = 0
artillery = Artillery(10, 10, ships)
fleet = Shipbuilder().getFleet(10, 10, ships)
print(fleet)
while fleetDestroyed == False:
    nbTries += 1
    field = artillery.shoot()
    column = chr(field._column + ord('A'))
    row = field._row + 1
    result = artillery.shoot()
    print("{} - {}".format(row, column))
    shootingResults = EnterScore()
    fleetDestroyed = artillery.processResults(shootingResults)

print("Fleet destroyed!")
print("After {0} tries".format(nbTries))
