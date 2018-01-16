import pandas as pd


def fix_person(person, text):
    ptokens = person.split()
    if len(ptokens) == 3:
        newp = '{} {}'.format(ptokens[0], ptokens[2])
        if newp in text:
            #  print("Removing middle name worked")
            return newp
        # Try last name only
        if ptokens[2] in text:
            return ptokens[2]
    if len(ptokens) == 2:
        # Try last name only
        if ptokens[1] in text:
            return ptokens[1]
        #  if ptokens[0] in text:
            #  print("First name only worked")
            #  print(person, text)
            #  return ptokens[0]
    if len(ptokens) > 3:
        if ptokens[-1] in text:
            return ptokens[-1]
    return None


def fix_pod(pod, text):
    commatokens = pod.split(', ')
    if len(commatokens) == 2:
        # city, state. Try just city. Then try just state
        if commatokens[0] in text:
            return commatokens[0]
    return None


if __name__ == "__main__":
    docs = pd.read_csv('pod.tsv', sep='\t', header=None,
                       names=['docid', 'text'])
    labels = pd.read_csv('pod_gold.tsv', sep='\t', header=None,
                         names=['docid', 'person', 'pod', 'label'])

    correct_labels = []

    combined = docs.merge(labels, on='docid')
    hits = 0
    person_misses = 0
    pod_misses = 0
    for _, row in combined.iterrows():
        docid = row['docid']
        person = row['person']
        pod = row['pod']
        text = row['text']

        # Simple fixes if person/pod not in text.
        if person not in text:
            person = fix_person(person, text)
            if person is None:
                person_misses += 1
                continue

        if pod not in text:
            pod = fix_pod(pod, text)
            if pod is None:
                pod_misses += 1
                continue

        hits += 1
        person_start = text.index(person)
        # XXX: snorkel spans don't use python slicing (i.e. up to end of range)
        # - so do minus 1 here
        person_end = person_start + len(person) - 1
        pod_start = text.index(pod)
        pod_end = pod_start + len(pod) - 1

        # Get stable ids
        person_sid = '{}::span:{}:{}'.format(docid, person_start, person_end)
        pod_sid = '{}::span:{}:{}'.format(docid, pod_start, pod_end)

        correct_labels.append(
            (person_sid, pod_sid, row['label']))

    print("Total", combined.shape[0], "after filtering", hits)
    print("Person misses", person_misses)
    print("pod misses", pod_misses)
    correct_df = pd.DataFrame.from_records(
        correct_labels, columns=['person', 'pod', 'label'])
    correct_df.to_csv('pod_gold_span.tsv', sep='\t', header=True,
                      index=False)
