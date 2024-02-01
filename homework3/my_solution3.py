def read_state_weights():
    with open('state_weights.txt') as file:
        file_lines = file.readlines()
        states = []
        states_and_weight = []
        header = file_lines[1].strip().split()
        state_num = int(header[0])

        for line in file_lines[2:]:
            states_info = line.strip().split(' ')
            state_name = states_info[0].strip('"')
            state_weight = float(states_info[1])
            states.append(state_name)
            states_and_weight.append([state_name, state_weight])
        return state_num, states, states_and_weight

def initial_state_probability(states_and_weight):
    total_weight = sum(weight for _, weight in states_and_weight)
    probabilities = []
    for state, weight in states_and_weight:
        probability = weight / total_weight
        probabilities.append([state, probability])
    return probabilities

def read_state_action_state_weights():
    with open('state_action_state_weights.txt') as file:
        file_lines = file.readlines()
        state_action_states = []
        header = file_lines[1].strip().split()
        num_triples = int(header[0])

        for line in file_lines[2:]:
            info = line.strip().split(' ')
            state = info[0].strip('"')
            action = info[1].strip('"')
            next_states = info[2].strip('"')
            weight = float(info[3])
            if action == "N":
                action = None
            state_action_states.append([state, action, next_states, weight])
        return num_triples, state_action_states

def calculate_transition_probabilities(state_action_states):
    total_weights = {}
    for state, action, _, weight in state_action_states:
        if (state, action) not in total_weights:
            total_weights[(state, action)] = 0
        total_weights[(state, action)] += weight

    probabilities = []
    for state, action, next_state, weight in state_action_states:
        probability = weight / total_weights[(state, action)]
        probabilities.append([state, action, next_state, probability])

    return probabilities

def read_state_observation_weights():
    with open('state_observation_weights.txt') as file:
        file_lines = file.readlines()
        state_observations = []
        header = file_lines[1].strip().split()
        num_pairs = int(header[0])

        for line in file_lines[2:]:
            info = line.strip().split(' ')
            state = info[0].strip('"')
            obs = info[1].strip('"')
            weight = float(info[2])
            state_observations.append([state, obs, weight])
        return num_pairs, state_observations

def observation_probabilities(state_observations):
    total_weights = {}
    for state, _, weight in state_observations:
        if state not in total_weights:
            total_weights[state] = 0
        total_weights[state] +=weight

    probabilities = []
    for state, obs, weight in state_observations:
        probability = weight / total_weights[state]
        probabilities.append([state, obs, probability])

    return probabilities

def read_observation_actions():
    with open('observation_actions.txt') as file:
        file_lines = file.readlines()
        obs_action = []
        num_seq = int(file_lines[1])

        for line in file_lines[2:]:
            info = line.strip().split(' ')

            if len(info) == 2:
                obs = info[0].strip('"')
                action = info[1].strip('"')
                if action == "N":
                    action = None

                obs_action.append([obs, action])
            elif len(info) == 1:
                obs = info[0].strip('"')
                obs_action.append([obs, None])
        return num_seq, obs_action

def convert_to_dict(prob_list):
    return {item[0]: item[1] for item in prob_list}

def convert_transition_prob(transition_list):
    trans_dict = {}
    for item in transition_list:
        state, action, next_state, prob = item
        if (state, action) not in trans_dict:
            trans_dict[(state, action)] = {}
        trans_dict[(state, action)][next_state] = prob
    return trans_dict

def convert_observation_prob(observation_list):
    obs_dict = {}
    for item in observation_list:
        state, obs, prob = item
        if state not in obs_dict:
            obs_dict[state] = {}
        obs_dict[state][obs] = prob
    return obs_dict

def viterbi(initial_prob, trans_prob, obs_prob, obs_act_seq):
    states = list(initial_prob.keys())

    V = [{}]
    path = {}

    for state in states:
        V[0][state] = initial_prob[state] * obs_prob[state].get(obs_act_seq[0][0], 0)
        path[state] = [state]

    for t in range(1, len(obs_act_seq)):
        V.append({})
        newpath = {}

        for cur_state in states:

            (prob, state) = max(
                (V[t-1][prev_state] *
                 trans_prob.get((prev_state, obs_act_seq[t-1][1]), {}).get(cur_state, 0) *
                 obs_prob[cur_state].get(obs_act_seq[t][0], 0), prev_state)
                for prev_state in states
            )

            V[t][cur_state] = prob
            newpath[cur_state] = path[state] + [cur_state]

        path = newpath

    (prob, state) = max((V[-1][state], state) for state in states)
    return (prob, path[state])

def output():
    _, states, states_and_weight = read_state_weights()
    initial_prob = initial_state_probability(states_and_weight)

    _, state_action_states = read_state_action_state_weights()
    transition_prob = calculate_transition_probabilities(state_action_states)

    _, state_obs = read_state_observation_weights()
    obs_prob = observation_probabilities(state_obs)
    _, obs_action_seq = read_observation_actions()

    initial_prob_dict = convert_to_dict(initial_prob)
    transition_prob_dict = convert_transition_prob(transition_prob)
    obs_prob_dict = convert_observation_prob(obs_prob)

    most_likely_states = viterbi(initial_prob_dict, transition_prob_dict, obs_prob_dict, obs_action_seq)[1]

    with open('states.txt', 'w') as file:
        file.write('states' + '\n')
        file.write(str(len(most_likely_states)) + '\n')
        for i in range(len(most_likely_states)):
            file.write('"' + str(most_likely_states[i]) + '"' + '\n')

output()
