import re

class Recipes:

    def __init__(self, input_file, index, allignment, vertical_sep, horizontal_sep, left_pad, right_pad) -> None:
        self.input_file = input_file
        self.index = index
        self.vertical_sep = vertical_sep
        self.horizontal_sep = horizontal_sep
        self.allignment = allignment
        self.left_padding = left_pad
        self.right_padding = right_pad
    
    def read_input_file(self,):
        self.combinations_dict = dict()
        with open(self.input_file, 'r') as input:
            for line in input:
                line = re.sub(r'\s+', '', line)
                if line.startswith('---'):
                    continue
                elif line.endswith(':'):
                    recipe = line[:-1]
                    ingredients = dict()
                else:
                    ingredient_name, ingredient_combinations = line.split("=")
                    ingredients[ingredient_name.strip()] = ingredient_combinations.split(",")
                self.combinations_dict[recipe] = ingredients

    def generate_combinations_with_index(self, input_list):
        if not input_list:
            return [[]]

        result = []
        for element in input_list[0]:
            sub_combinations = self.generate_combinations_with_index(input_list[1:])
            for sub_combination in sub_combinations:
                result.append([element] + sub_combination)

        return result

    def generate_combinations(self):
        self.generated_combinations = dict()
        
        for receipe in self.combinations_dict:
            combinations_list = list()
            for ingredient in self.combinations_dict[receipe]:
                combinations_list.append(self.combinations_dict[receipe][ingredient])
            
            first_line = [f"{self.index}"]
            first_line.extend(self.combinations_dict[receipe].keys())
            combinations = self.generate_combinations_with_index(combinations_list)
            for index, each_list in enumerate(combinations, start=1):
                each_list.insert(0, index)
            combinations.insert(0, first_line)
            self.generated_combinations[receipe] = combinations
     
    def get_max_length(self, input_list):
        max_lengths = [0] * len(input_list[0])
        for sublist in input_list:
            for idx, item in enumerate(sublist):
                item_len = len(str(item))
                if item_len > max_lengths[idx]:
                    max_lengths[idx] = item_len

        return max_lengths
    
    def format_strings(self, string, max_length):
        length_string = len(string)
        pad_length = max_length - length_string

        if pad_length <= 0:
            return string

        if self.allignment == 'left':
            padded_string = string + ' ' * pad_length
        elif self.allignment == 'right':
            padded_string = ' ' * pad_length + string
        elif self.allignment == 'center':
            left_pad = pad_length // 2
            right_pad = pad_length - left_pad
            padded_string = ' ' * left_pad + string + ' ' * right_pad
        else:
            padded_string = string

        return padded_string
    
    def get_horizontal_line(self, input_list):
        string = ""
        for multiplier in input_list:
            string = string + self.vertical_sep
            string = string + self.horizontal_sep * multiplier
        string = string + self.vertical_sep
        return string
    
    def add_padding(self):
        for receipe in self.generated_combinations:
            for comb_index, combination_list in enumerate(self.generated_combinations[receipe]):
                for ingredient_index, ingredient in enumerate(combination_list):
                    ingredient_with_pad = ' ' *self.left_padding + f"{ingredient}" + ' ' * self.right_padding
                    self.generated_combinations[receipe][comb_index][ingredient_index] = ingredient_with_pad
    

    def write_output_files(self):
        self.add_padding()
        for receipe in self.generated_combinations:
            combinations = self.generated_combinations[receipe]
            max_length = self.get_max_length(combinations)
            horizontal_line = self.get_horizontal_line(max_length)
            with open(f"{receipe}_ingredients_combinations.txt", 'w') as output:
                output.write(f"{receipe} Recipes")
                output.write('\n')
                output.write('\n')
                output.write(horizontal_line)
                output.write('\n')
                for combination_list in combinations:
                    for index, ingredient in enumerate(combination_list):
                        output.write(self.vertical_sep)
                        output.write(self.format_strings(f"{ingredient}", max_length[index]))
                    output.write(self.vertical_sep)
                    output.write('\n')
                    output.write(horizontal_line)
                    output.write('\n')

def main():
    recipes = Recipes(input_file, index, allignment, vertical_sep, horizontal_sep, left_padding, right_padding)
    recipes.read_input_file()
    recipes.generate_combinations()
    recipes.write_output_files()


if __name__ == "__main__":
    input_file = "recipes_input_data.txt"
    index = "Combinations"
    vertical_sep = "|"
    horizontal_sep = "-"
    allignment = 'center'
    left_padding = 2
    right_padding = 2

    main()