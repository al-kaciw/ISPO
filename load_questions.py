import csv


def load_questions_from_csv(file_path, start_pos, max_pos):
    questions = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            # Skip rows up to start_pos
            for _ in range(start_pos):
                next(reader, None)

            for index, row in enumerate(reader):
                if index >= (max_pos - start_pos):  # Stop at max_pos
                    break
                questions.append({
                    'question': row['question'],
                    'answer': row['answer'],
                    'explanation': row['explanation'],
                    'index': start_pos + index
                })
    except (FileNotFoundError, KeyError) as e:
        print(f"Error loading questions: {e}")
    return questions


def get_questions(section_index):
    """Loads questions based on predefined topic distribution."""

    questions = []
    file_path = f'assets/questions/section{section_index}.csv'
    start_pos = 0
    for topic in section_distributions[section_index]:
        max_pos = start_pos + topic  # Correctly calculate max_pos
        questions.append(load_questions_from_csv(file_path, start_pos, max_pos))
        start_pos = max_pos  # Update start_pos for the next topic

    return questions


section_distributions = [[7, 4, 5, 5, 5],
                         [5, 5, 6, 7, 5]]

# Run only if executed directly
if __name__ == "__main__":

    for j in range(2):
        question = get_questions(j)
        for i, topic_questions in enumerate(question):
            print(f"Topic {i + 1 + j * 5}:")
            for q in topic_questions:
                print(q)
