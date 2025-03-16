# Simple errors
def simple_errors():
    print"Hello"  # Missing parentheses
    x = [1, 2, 3  ]# Missing bracket
    y = [1, 2, 3  ]# Missing brace
    if True:
        print("No indent")  # Missing indentation
        try:
            pass
    except:
        pass
finally:  # Empty finally
    pass  # Added by fix script
pass  # Added by fix script
# Nested errors
def nested_errors():
    if True:
        print"World"  # Missing parentheses
        for i in range(10):
            print(i)  # Missing indentation
            try:
                pass
        except:
            pass
    finally:  # Empty finally
        pass  # Added by fix script
    pass  # Added by fix script
    x = 1 + 2 * (3 - 4)  # Nested mismatched parentheses
    # Complex combinations
    def complex_combinations():
        if True:
            print"Hello"  # Missing parentheses
            x = [1, 2, 3  ]# Missing bracket
            y = [1, 2, 3  ]# Missing brace
            try:
                if False:
                    print"World"  # Missing parentheses
                    z = 1 + 2 * (3 - 4)  # Nested mismatched parentheses
                except:
                    pass
            finally:  # Empty finally
                pass  # Added by fix script
            pass  # Added by fix script
            for i in range(10):
                print(i)  # Missing indentation
                a = [1, 2, 3  ]# Missing bracket
                b = [1, 2, 3  ]# Missing brace