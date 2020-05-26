import logging

## Setting up logging for Debug messages
FORMAT = "%(message)s"
logging.basicConfig(format=FORMAT)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

## Constants
TRUE = 1
FALSE = 0

INSTRUCTIONS = {
    "add", 
    "negate", 
    "equal", 
    "zero", 
    "one", 
    "loadcon", 
    "br", 
    "br_false",
    "dup",
    "mpy",
    "write",
    "swap",
    "less"}

class Stack:
    """ Implementation of stack abstract data type
    Supports push, pop and len operations
    """
    
    def __init__(self, size_limit, elements=[]):
        self._stack_elements = []
        self._size_limit = size_limit
        if len(elements) > size_limit:
            raise Exception("Stack elements exceed stack size limit")
        if len(elements) > 0:
            self._stack_elements.extend(elements)
    
    def get_stack_elements(self):
        return self._stack_elements

    def pop(self):
        if len(self._stack_elements) > 0:
            return self._stack_elements.pop(-1)
        return None
    
    def push(self, elem):
        if len(self._stack_elements) + 1 > self._size_limit:
            print("The stack is full, could not push " + str(elem))
            return 
        self._stack_elements.append(elem)
    
    def __len__(self):
        return len(self._stack_elements)
    
    def __str__(self):
        return f"Stack with {self._stack_elements}"
    
    def __repr__(self):
        return f"Stack({self._size_limit}, {self._stack_elements})"


class Instruction:
    def __init__(self, instruction_name, instruction_value=None):
        """Only loadcon instructions have a value
            Parameters:
                instruction_name (str): the name of the instruction, 
                should be in the INSTRUCTIONS set
                instructions_value (int): (None for all non-load con instructions, else int)
        """
        if instruction_name not in INSTRUCTIONS:
            raise Exception("Invalid instruction: ", instruction_name)

        self._instruction_name = instruction_name
        self._instruction_value = instruction_value

        if "loadcon" not in instruction_name and instruction_value is not None:
            raise Exception("Unexpected instruction value given for non LOADCON call")
    
    def get_instruction_name(self):
        return self._instruction_name

    def get_instruction_value(self):
        return self._instruction_value

    def __repr__(self):
        value = "" if not self._instruction_value else f" {self._instruction_value}"
        return self._instruction_name + value


class StackMachine:
    def __init__(self, instructions, stack_size= 10):
        self._value_stack = Stack(stack_size)
        self._size_limit = stack_size
        self._instructions = instructions
        self._program_counter = 0 # the address of the next machine instruction
    
    def get_value_stack(self):
        return self._value_stack
    
    def display(self):
        """
        Prints out a representation of the stack machine
        e.g.
        for a stack of values: (bottom) 1,2,3 (top)
        prints:

            TOP
        -----------------
                3
        -----------------
                2
        -----------------
                1
        -----------------
            BOTTOM
        """

        row = "----------------\n"
        margins = "\t"
        output = ["\n"]

        output.append(margins)
        output.append("TOP\n")

        for elem in self._value_stack.get_stack_elements()[::-1]:
            output.append(row)
            output.append(margins)
            output.append(str(elem))
            output.append("\n")
        
        output.append(row)
        output.append(margins)
        output.append("BOTTOM\n\n")

        output = "".join(output)
        
        print(output)
    
    
    def run(self):
        logging.info("Starting Execution of Stack Machine")
        
        while True:
            if not (self._program_counter > (len(self._instructions) - 1)):
                current_instruction = self._instructions[self._program_counter]
            else:
                break

            logging.info("Executing: %s", current_instruction)

            func = getattr(self, current_instruction.get_instruction_name(), None)

            if current_instruction.get_instruction_name() == "loadcon":
                func(current_instruction.get_instruction_value())
            else:
                func()
            
            self.display()
            self._program_counter += 1

        logging.info("Execution has finished")
    
    def loadcon(self, value):
        self._value_stack.push(value)
    
    def br(self):
        # todo add checks for ranges on br calls
        if len(self._value_stack) < 1:
            logging.info("Stack too small to execute br")
            return
        
        offset_index = self._value_stack.pop()
        self._program_counter += offset_index
    
    def br_false(self):
        if len(self._value_stack) < 2:
            logging.info("Stack too small to execute br_false")
            return
        
        offset_index = self._value_stack.pop()
        check_condition = self._value_stack.pop()

        if check_condition != TRUE:
            self._program_counter += offset_index

    def add(self):
        """Adds the top two elements on the stack. 
        Returns the result on the top of the stack"""
        if len(self._value_stack) < 2:
            logging.info("Stack too small to execute add")
            return
        value_1 = self._value_stack.pop()
        value_2 = self._value_stack.pop()
        
        self._value_stack.push(value_1 + value_2)
    
    def negate(self):
        """Negates the top of the stack value"""
        if len(self._value_stack) < 1:
            return
        value_1 = self._value_stack.pop() * -1
        self._value_stack.push(value_1)
    
    def equal(self):
        if len(self._value_stack) < 2:
            return
        value_1 = self._value_stack.pop()
        value_2 = self._value_stack.pop()

        if value_1 == value_2:
            self._value_stack.push(TRUE)
        else:
            self._value_stack.push(FALSE)
    
    def less(self):
        if len(self._value_stack) < 2:
            return
        top = self._value_stack.pop()
        second_top = self._value_stack.pop()

        if second_top < top:
            self._value_stack.push(TRUE)
        else:
            self._value_stack.push(FALSE)
    
    def swap(self):
        if len(self._value_stack) < 2:
            return
        value_1 = self._value_stack.pop()
        value_2 = self._value_stack.pop()

        self._value_stack.push(value_1)
        self._value_stack.push(value_2)
    
    def mpy(self):
        """Multiplies the top two elements on the stack. 
        Returns the result on the top of the stack"""
        if len(self._value_stack) < 2:
            logging.info("Stack too small to execute add")
            return
        value_1 = self._value_stack.pop()
        value_2 = self._value_stack.pop()
        
        self._value_stack.push(value_1 * value_2)
    
    def zero(self):
        self._value_stack.push(0)
    
    def one(self):
        self._value_stack.push(1)
    
    def write(self):
        if len(self._value_stack) < 1:
            logging.info("Stack too small to execute write")
            return
        
        value = self._value_stack.pop()
        print("\t\t\t", value)
    
    def dup(self):
        if len(self._value_stack) < 1:
            logging.info("Stack too small to execute dup")
            return
        
        value = self._value_stack.pop()
        self._value_stack.push(value)
        self._value_stack.push(value)
    
    def __str__(self):
        return f"Stack Machine\n\tInstructions: {self._instructions}\n\tStack Values: {self._value_stack}"
    
    def __repr__(self):
        return f"StackMachine({self._instructions}, {self._size_limit})"


def convert_list_to_instructions(instructions):
    conv_instructions = []
    for instruction in instructions:
        x = instruction.split(" ")
        if len(x) == 2:
            instruction_name = x[0].lower()
            instruction_value = int(x[1])
            conv_instructions.append(Instruction(instruction_name, instruction_value))
        else:
            conv_instructions.append(Instruction(instruction.lower()))
    return conv_instructions

def main():
    # print("This is an interactive absolute function calculator built on a stack machine")
    # input_number = input("What number would you like to get the abs value of?:\t")

    # absolute_fn = [f"loadcon {input_number}", "dup", "zero", "less", "loadcon 3", "br_false", "one", "negate", "mpy", "write"]
    
    absolute_fn = ["loadcon 2", "loadcon 3", "negate", "add", "write"]

    instructions = convert_list_to_instructions(absolute_fn)
    sm = StackMachine(instructions)
    sm.run()
    print(sm)

    input("Press any key to close...")


if __name__ == "__main__":
    main()






# Possible areas to extend:
# todo take instructions from user input in interactive mode
# todo use alloc calls for variable values
# todo implement store and load frame
