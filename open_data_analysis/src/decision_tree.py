# Split a dataset based on an attribute and an attribute value
def test_split(index, value, var_name, dataset):
    # print 'test_split: index={}, var={}, value={}'.format(index, var_name, value)
    left, right = list(), list()
    for row in dataset:
        if row[index] == value:
            left.append(row)
        else:
            right.append(row)
    return left, right


def gini_imp(groups):
    s = 0
    for group in groups:
        c = Counter([row[-1] for row in group])
        total = len(group)
        gi = 1
        for v in c.values():
            gi -= (v * 1.0 / total) ** 2
        s += gi * total
    return s


# Select the best split point for a dataset
def get_split(dataset, var_names, debug=False):
    class_values = list(set(row[-1] for row in dataset))
    # print class_values
    b_index, b_value, b_score, b_groups = 999, 999, 999, None
    for index in range(len(dataset[0]) - 1):
        var_name = var_names[index]
        var_value_set = list(set([row[index] for row in dataset]))
        # print 'var =', var_name, 'var_value_set:', var_value_set, 'previous b_score="{}".'.format(b_score)
        for var_v in var_value_set:
            groups = test_split(index, var_v, var_name, dataset)
            # gini = gini_index(groups, class_values)
            gini = gini_imp(groups)
            # if gini<b_score and debug or var_name=='sidewalk':
            if gini < b_score and debug:
                print '{}=="{}" vs {}=="{}"'.format(var_name, var_v, var_names[b_index] if b_index != 999 else b_index,
                                                    b_value), ':', gini, 'vs', b_score, gini < b_score
            if gini < b_score:
                b_index, b_value, b_score, b_groups = index, var_v, gini, groups
    return {'index': b_index, 'value': b_value, 'groups': b_groups}


# Create a terminal node value
def to_terminal(group):
    outcomes = [row[-1] for row in group]
    # print 'to_terminal', set(outcomes), max(set(outcomes), key=outcomes.count), dict(Counter(outcomes))
    return (max(set(outcomes), key=outcomes.count))
    # return (max(set(outcomes), key=outcomes.count),Counter(outcomes))


from collections import Counter


# Create child splits for a node or make terminal
def split(node, var_names, max_depth, min_size, depth, debug=False):
    left, right = node['groups']
    del (node['groups'])
    left_outcomes = set([row[-1] for row in left])
    right_outcomes = set([row[-1] for row in right])
    total_outcomes = right_outcomes | left_outcomes
    if debug:
        print depth, node['index'], var_names[node['index']], node['value'], len(left), len(right), len(left + right)
        print left_outcomes, right_outcomes, total_outcomes

    if len(total_outcomes) == 1:
        if debug: print depth, 'one total outcome'
        node['left'] = node['right'] = to_terminal(left + right)
        return
    elif len(left_outcomes) == 1 and len(right_outcomes) == 1:
        if debug: print depth, 'one left outcome, one other right outcome'
        node['left'] = to_terminal(left)
        node['right'] = to_terminal(right)
        return

    # check for a no split
    if not left or not right:
        if debug: print depth, 'no left, no right'
        node['left'] = node['right'] = to_terminal(left + right)
        return
    # check for max depth
    if depth >= max_depth:
        if debug: print depth, '>=max depth'
        node['left'], node['right'] = to_terminal(left), to_terminal(right)
        return
    # process left child
    if len(left_outcomes) == 1:
        if debug: print depth, 'one left outcomes'
        node['left'] = to_terminal(left)
    elif len(left) <= min_size:
        if debug: print depth, '-->left, reach min size'
        node['left'] = to_terminal(left)
    else:
        if debug: print depth, '-->left, continue recurse'
        node['left'] = get_split(left, var_names, debug)
        split(node['left'], var_names, max_depth, min_size, depth + 1, debug)
    # process right child
    if len(right_outcomes) == 1:
        if debug: print depth, 'one right outcome'
        node['right'] = to_terminal(right)
    elif len(right) <= min_size:
        if debug: print depth, '-->right, reach min size'
        node['right'] = to_terminal(right)
    else:
        if debug: print depth, '-->right, continue recurse'
        node['right'] = get_split(right, var_names, debug)
        split(node['right'], var_names, max_depth, min_size, depth + 1, debug)


# Build a decision tree
def build_tree(train, var_names, max_depth, min_size, debug=False):
    if debug:  print 'getting root'
    root = get_split(train, var_names, debug)
    if debug:  print 'got root'
    split(root, var_names, max_depth, min_size, 1, debug)
    return root


# Print a decision tree
def print_tree(node, var_names, depth=0):
    if isinstance(node, dict):
        print('{}. {}[{} = {}]'.format(depth, depth * '\t', var_names[node['index']], node['value']))
        print_tree(node['left'], var_names, depth=depth + 1)
        print('{}. {}[{} != {}]'.format(depth, depth * '\t', var_names[node['index']], node['value']))
        print_tree(node['right'], var_names, depth=depth + 1)
    else:
        print('{}. {}-->{}'.format(depth, depth * '\t', node))

def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False


def print_py_func(node, var_names, depth=0):
    rows = []
    if isinstance(node, dict):
        key, value = var_names[node['index']], node['value']
        rows.append("    {}if tags['{}'] == '{}':".format(depth * '    ', key, value))
        rows.extend(print_py_func(node['left'], var_names, depth=depth + 1))
        rows.append("    {}else:  # tags['{}'] != '{}'".format(depth * '    ', key, value))
        rows.extend(print_py_func(node['right'], var_names, depth=depth + 1))
    else:
        if isfloat(node):
            rows.append("    {}return {}".format(depth * '    ', node))
        else:
            rows.append("    {}return '{}'".format(depth * '    ', node))
    return rows

# def print_py_func(node, var_names, depth=0):
#
#     if isinstance(node, dict):
#         key, value = var_names[node['index']], node['value']
#         print("    {}if tags['{}'] == '{}':".format(depth * '    ', key, value))
#         print_py_func(node['left'], var_names, depth=depth + 1)
#         print("    {}else:  # tags['{}'] != '{}'".format(depth * '    ', key, value))
#         print_py_func(node['right'], var_names, depth=depth + 1)
#     else:
#         print("    {}return '{}'".format(depth * '    ', node))
#

# Make a prediction with a decision tree
def predict(node, row):
    if row[node['index']] == node['value']:
        if isinstance(node['left'], dict):
            return predict(node['left'], row)
        else:
            return node['left']
    else:
        if isinstance(node['right'], dict):
            return predict(node['right'], row)
        else:
            return node['right']


# Classification and Regression Tree Algorithm
def decision_tree(train, test, var_names, max_depth, min_size):
    tree = build_tree(train, var_names, max_depth, min_size)
    predictions = list()
    for row in test:
        prediction = predict(tree, row)
        predictions.append(prediction)
    return (predictions)


# Calculate accuracy percentage
def accuracy_metric(actual, predicted, debug=False):
    correct = 0
    for i in range(len(actual)):
        if actual[i] == predicted[i]:
            correct += 1
        elif debug:
            print i, actual[i], predicted[i]
    return correct / float(len(actual)) * 100.0
