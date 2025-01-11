from docx import Document
from datasets import Dataset
from transformers import GPT2Tokenizer, GPT2LMHeadModel, Trainer, TrainingArguments

# Step 1: Extract Text from the MoM .docx file
def extract_text_from_docx(docx_file):
    document = Document(docx_file)
    full_text = []
    for para in document.paragraphs:
        full_text.append(para.text)
    return "\n".join(full_text)

# Step 2: Load and Format Conversation Data for Training
def create_training_data(conversation_file, mom_text):
    with open(conversation_file, 'r', encoding='utf-8') as file:
        conversation = file.readlines()
    
    # Format conversation and MOM into input-output pairs
    training_data = []
    for line in conversation:
        training_data.append({
            'text': line.strip() + '\n' + mom_text  # Combining conversation and MOM text
        })
    return training_data

# Step 3: Tokenizing the Dataset
def tokenize_function(examples):
    return tokenizer(examples['text'], padding="max_length", truncation=True)

# Step 4: Train the Model
def train_model(training_data):
    # Convert to Hugging Face Dataset
    dataset = Dataset.from_dict({'text': [item['text'] for item in training_data]})

    # Load GPT-2 tokenizer and model
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    model = GPT2LMHeadModel.from_pretrained('gpt2')

    # Tokenize the dataset
    tokenized_dataset = dataset.map(tokenize_function, batched=True)

    # Setup Training Arguments
    training_args = TrainingArguments(
        output_dir='./results',  # Output directory for the model
        num_train_epochs=3,      # Number of epochs to train
        per_device_train_batch_size=2,  # Training batch size
        per_device_eval_batch_size=2,   # Evaluation batch size
        logging_dir='./logs',    # Directory for logs
        save_steps=1000,         # Save the model every 1000 steps
    )

    # Initialize Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
    )

    # Train the model
    trainer.train()

    return model, tokenizer

# Step 5: Generate MOM for New Conversation
def generate_mom_for_new_conversation(model, tokenizer, conversation_text):
    inputs = tokenizer.encode(conversation_text, return_tensors="pt")
    outputs = model.generate(inputs, max_length=500, num_return_sequences=1)
    generated_mom = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return generated_mom

# Step 6: Save the Generated MOM as a .docx File
def save_mom_to_docx(mom_content, output_file):
    document = Document()
    document.add_heading('Minutes of Meeting', level=1)
    document.add_paragraph(mom_content)
    document.save(output_file)
    print(f"MOM saved successfully as {output_file}")

# Main execution
if __name__ == "__main__":
    conversation_file = '02-01-2025-15-34-05_transcription.txt'  # Path to your new conversation file
    mom_file = 'MoM 1.docx'  # Path to your MoM document

    # Extract MOM text from MoM 1.docx
    mom_text = extract_text_from_docx(mom_file)

    # Create the training dataset
    training_data = create_training_data(conversation_file, mom_text)

    # Train the model
    model, tokenizer = train_model(training_data)

    # Read the conversation from the new conversation file
    with open(conversation_file, 'r', encoding='utf-8') as file:
        new_conversation = file.read()

    # Generate the MOM
    generated_mom = generate_mom_for_new_conversation(model, tokenizer, new_conversation)
    print("\nGenerated MOM:\n", generated_mom)

    # Save the generated MOM to a Word document
    save_mom_to_docx(generated_mom, "Generated_MOM.docx")
