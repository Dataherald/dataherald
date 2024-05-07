Finetuning Module
===================

The finetuning module plays a crucial role, encompassing three primary functions: implementing the database schema serialization method, generating the finetuning dataset, and conducting finetuning of a Large Language Model (LLM) on the curated dataset.

Each family of LLMs necessitates a unique serialization method tailored to optimize its performance. This customization ensures that the serialization process aligns perfectly with the specific architectural nuances and processing capabilities of each LLM family. At present, our focus is on the GPT family of models, as provided by OpenAI. These models, known for their advanced NL2SQL capabilities.

Abstract finetuning Class
--------------------------

All implementations of the context store must inherit from the abstract :class:`FinetuningModel` class and implement the following methods.

:class:`FinetuningModel`
^^^^^^^^^^^^^^^^^^^^^^^^

This class serves as an abstract base for fine-tuning models, providing a structured framework for managing the fine-tuning process.

.. py:class:: FinetuningModel(storage)
   :noindex:

   Initializes the FinetuningModel instance with the application storage.

   :param storage: The storage system
   :type storage: DB

.. py:method:: count_tokens(self, messages: dict) -> int
   :noindex:
   :abstractmethod:

   Counts the number of tokens in the provided messages, a necessary step in preparing data for fine-tuning. We need this information primarily to avoid exceeding the maximum token limit of the model.

   :param messages: A dictionary containing messages (system, user, assistant) to be tokenized.
   :type messages: dict
   :return: The total count of tokens.
   :rtype: int

.. py:method:: create_fintuning_dataset(self)
   :noindex:
   :abstractmethod:

   Abstract method to create a dataset suitable for fine-tuning. This involves processing and structuring data according to the model's requirements.

.. py:method:: create_fine_tuning_job(self)
   :noindex:
   :abstractmethod:

   Initiates a fine-tuning job. This method should encompass all the necessary steps to start the fine-tuning process on the prepared dataset.

.. py:method:: retrieve_finetuning_job(self) -> Finetuning
   :noindex:
   :abstractmethod:

   Retrieves the current status or results of a fine-tuning job.

   :return: An instance of the Finetuning class representing the finetuning job.
   :rtype: Finetuning

.. py:method:: cancel_finetuning_job(self) -> Finetuning
   :noindex:
   :abstractmethod:

   Cancels an ongoing fine-tuning job.

   :return: An updated instance of the Finetuning class reflecting the job's cancellation.
   :rtype: Finetuning

