def cycle_lane_assignment(tags):
    if tags['cycleway'] == 'lane':
        if tags['oneway'] == 'yes':
            if tags['highway'] == 'cycleway':
                return ''
            else:  # tags['highway'] != 'cycleway'
                return 'one'
        else:  # tags['oneway'] != 'yes'
            return 'both'
    else:  # tags['cycleway'] != 'lane'
        if tags['cycleway:right'] == '':
            if tags['cycleway'] == 'shared_lane':
                if tags['oneway'] == '':
                    return 'both'
                else:  # tags['oneway'] != ''
                    return 'one'
            else:  # tags['cycleway'] != 'shared_lane'
                if tags['cycleway'] == 'opposite_lane':
                    return 'both'
                else:  # tags['cycleway'] != 'opposite_lane'
                    if tags['cycleway:left'] == '':
                        if tags['oneway:bicycle'] == '':
                            if tags['sidewalk'] == 'no':
                                if tags['highway'] == 'tertiary':
                                    return ''
                                else:  # tags['highway'] != 'tertiary'
                                    return ''
                            else:  # tags['sidewalk'] != 'no'
                                return ''
                        else:  # tags['oneway:bicycle'] != ''
                            return 'both'
                    else:  # tags['cycleway:left'] != ''
                        return 'both'
        else:  # tags['cycleway:right'] != ''
            if tags['cycleway:left'] == '':
                if tags['oneway'] == '':
                    if tags['cycleway:right'] == 'lane':
                        return 'one'
                    else:  # tags['cycleway:right'] != 'lane'
                        return 'right'
                else:  # tags['oneway'] != ''
                    if tags['cycleway:right'] == 'lane':
                        return 'right'
                    else:  # tags['cycleway:right'] != 'lane'
                        if tags['highway'] == 'residential':
                            return 'both'
                        else:  # tags['highway'] != 'residential'
                            return ''
            else:  # tags['cycleway:left'] != ''
                if tags['cycleway:left'] == 'shared_lane':
                    return 'one'
                else:  # tags['cycleway:left'] != 'shared_lane'
                    return 'both'


def is_shared_assignment(tags):
    if tags['cycleway'] == 'shared_lane':
        if tags['lanes'] == '4':
            if tags['highway'] == 'tertiary':
                if tags['sidewalk'] == '':
                    return ''
                else:  # tags['sidewalk'] != ''
                    return 1.0
            else:  # tags['highway'] != 'tertiary'
                return 1.0
        else:  # tags['lanes'] != '4'
            return 1.0
    else:  # tags['cycleway'] != 'shared_lane'
        if tags['cycleway:right'] == 'shared_lane':
            return 1.0
        else:  # tags['cycleway:right'] != 'shared_lane'
            if tags['oneway:bicycle'] == '':
                if tags['sidewalk'] == 'no':
                    if tags['highway'] == 'tertiary':
                        if tags['bicycle'] == '':
                            return ''
                        else:  # tags['bicycle'] != ''
                            return 1.0
                    else:  # tags['highway'] != 'tertiary'
                        return ''
                else:  # tags['sidewalk'] != 'no'
                    return ''
            else:  # tags['oneway:bicycle'] != ''
                if tags['highway'] == 'residential':
                    return 1.0
                else:  # tags['highway'] != 'residential'
                    return ''


def cycle_way_assignment(tags):
    if tags['highway'] == 'cycleway':
        if tags['oneway'] == 'yes':
            return 'one'
        else:  # tags['oneway'] != 'yes'
            if tags['cycleway'] == 'track':
                return 'one'
            else:  # tags['cycleway'] != 'track'
                return 'both'
    else:  # tags['highway'] != 'cycleway'
        if tags['cycleway'] == 'track':
            return 'both'
        else:  # tags['cycleway'] != 'track'
            if tags['cycleway:right'] == 'track':
                return 'right'
            else:  # tags['cycleway:right'] != 'track'
                return ''


def side_walk_assignment(tags):
    if tags['sidewalk'] == '':
        if tags['highway'] == 'trunk':
            if tags['foot'] == 'yes':
                return 'right'
            else:  # tags['foot'] != 'yes'
                return ''
        else:  # tags['highway'] != 'trunk'
            return ''
    else:  # tags['sidewalk'] != ''
        if tags['sidewalk'] == 'both':
            return 'both'
        else:  # tags['sidewalk'] != 'both'
            if tags['sidewalk'] == 'right':
                if tags['cycleway'] == '':
                    if tags['cycleway:left'] == '':
                        return 'right'
                    else:  # tags['cycleway:left'] != ''
                        return 'both'
                else:  # tags['cycleway'] != ''
                    if tags['oneway'] == '':
                        return 'both'
                    else:  # tags['oneway'] != ''
                        return 'right'
            else:  # tags['sidewalk'] != 'right'
                if tags['sidewalk'] == 'left':
                    if tags['highway'] == 'footway':
                        return ''
                    else:  # tags['highway'] != 'footway'
                        return 'left'
                else:  # tags['sidewalk'] != 'left'
                    if tags['sidewalk'] == 'yes':
                        if tags['highway'] == 'footway':
                            return ''
                        else:  # tags['highway'] != 'footway'
                            if tags['highway'] == 'pedestrian':
                                return ''
                            else:  # tags['highway'] != 'pedestrian'
                                return 'both'
                    else:  # tags['sidewalk'] != 'yes'
                        if tags['sidewalk'] == 'separate':
                            return 'both'
                        else:  # tags['sidewalk'] != 'separate'
                            if tags['bicycle'] == '':
                                if tags['highway'] == 'footway':
                                    return ''
                                else:  # tags['highway'] != 'footway'
                                    return 'no'
                            else:  # tags['bicycle'] != ''
                                if tags['oneway'] == '':
                                    return 'no'
                                else:  # tags['oneway'] != ''
                                    return ''


def bikable_assignment(tags):
    if tags['bicycle'] == '':
        if tags['foot'] == '':
            if tags['highway'] == 'footway':
                return 'yes'
            else:  # tags['highway'] != 'footway'
                if tags['highway'] == 'pedestrian':
                    return 'yes'
                else:  # tags['highway'] != 'pedestrian'
                    if tags['highway'] == 'path':
                        return 'yes'
                    else:  # tags['highway'] != 'path'
                        if tags['highway'] == 'track':
                            return 'no'
                        else:  # tags['highway'] != 'track'
                            if tags['cycleway'] == 'no':
                                return 'no'
                            else:  # tags['cycleway'] != 'no'
                                return ''
        else:  # tags['foot'] != ''
            if tags['foot'] == 'no':
                if tags['sidewalk'] == 'right':
                    return ''
                else:  # tags['sidewalk'] != 'right'
                    if tags['highway'] == 'cycleway':
                        return ''
                    else:  # tags['highway'] != 'cycleway'
                        if tags['sidewalk'] == 'none':
                            return ''
                        else:  # tags['sidewalk'] != 'none'
                            return 'no'
            else:  # tags['foot'] != 'no'
                if tags['sidewalk'] == '':
                    if tags['highway'] == 'cycleway':
                        return ''
                    else:  # tags['highway'] != 'cycleway'
                        if tags['highway'] == 'trunk':
                            return ''
                        else:  # tags['highway'] != 'trunk'
                            if tags['cycleway'] == '':
                                if tags['highway'] == 'steps':
                                    return 'yes'
                                else:  # tags['highway'] != 'steps'
                                    return 'yes'
                            else:  # tags['cycleway'] != ''
                                return ''
                else:  # tags['sidewalk'] != ''
                    if tags['highway'] == 'pedestrian':
                        return 'yes'
                    else:  # tags['highway'] != 'pedestrian'
                        return ''
    else:  # tags['bicycle'] != ''
        if tags['bicycle'] == 'no':
            if tags['highway'] == 'cycleway':
                return ''
            else:  # tags['highway'] != 'cycleway'
                if tags['lanes'] == '1':
                    if tags['highway'] == 'motorway':
                        return 'yes'
                    else:  # tags['highway'] != 'motorway'
                        return 'no'
                else:  # tags['lanes'] != '1'
                    return 'no'
        else:  # tags['bicycle'] != 'no'
            if tags['cycleway'] == '':
                if tags['highway'] == 'cycleway':
                    return ''
                else:  # tags['highway'] != 'cycleway'
                    if tags['bicycle'] == 'dismount':
                        if tags['highway'] == 'pedestrian':
                            return 'no'
                        else:  # tags['highway'] != 'pedestrian'
                            return 'yes'
                    else:  # tags['bicycle'] != 'dismount'
                        if tags['sidewalk'] == 'no':
                            if tags['highway'] == 'tertiary':
                                return ''
                            else:  # tags['highway'] != 'tertiary'
                                return 'yes'
                        else:  # tags['sidewalk'] != 'no'
                            return 'yes'
            else:  # tags['cycleway'] != ''
                if tags['cycleway'] == 'no':
                    return 'yes'
                else:  # tags['cycleway'] != 'no'
                    return ''


