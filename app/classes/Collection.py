from app.scripts.helpers import get_field


class Metadata:
    def __init__(
        self, training_data, training_techniques, training_resources, architecture
    ):
        self.training_data = str(training_data)
        self.training_techniques = str(training_techniques)
        self.training_resources = str(training_resources)
        self.architecture = str(architecture)

    def __str__(self):
        techniques_str = ", ".join(self.training_techniques)
        architecture_str = ", ".join(self.architecture)

        return f"Training Data: {self.training_data}\nTraining Techniques: {techniques_str}\nTraining Resources: {self.training_resources}\nArchitecture: {architecture_str}"


class Collection:
    def __init__(self, name, metadata="", paper="", readme="", code=""):
        self.name = name
        self.metadata = Metadata(
            get_field(metadata, "Training Data"),
            get_field(metadata, "Training Techniques"),
            get_field(metadata, "Training Resources"),
            get_field(metadata, "Architecture"),
        )
        self.paper = paper
        self.readme = readme
        self.code = code
        self.models = []

    def add_model(self, model):
        self.models.append(model)

    def __str__(self):
        paper_str = ", ".join([f"{key}: {value}" for key, value in self.paper.items()])
        code_str = ", ".join([f"{key}: {value}" for key, value in self.code.items()])
        models_str = "\n".join([f"- {model}" for model in self.models])
        return f"Name: {self.name}\nMetadata: {self.metadata}\nPaper: {paper_str}\nREADME: {self.readme}\nCode: {code_str}\nModels:\n{models_str}"
