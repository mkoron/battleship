import random

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

maj3 = Shipbuilder()
fleet = maj3.getFleet(10, 10, [5, 4, 4, 3, 3, 3, 2, 2, 2, 2])
print(fleet)