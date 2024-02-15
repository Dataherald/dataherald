import pymongo

import config

if __name__ == "__main__":
    data_store = pymongo.MongoClient(config.db_settings.mongodb_uri)[
        config.db_settings.mongodb_db_name
    ]

    # Update all prompts to have a source
    mddh_prefix = "metadata.dh_internal"
    slack_prompts = data_store["prompts"].update_many(
        {
            f"{mddh_prefix}.slack_info": {"$exists": True},
            "$or": [
                {f"{mddh_prefix}.playground": False},
                {f"{mddh_prefix}.playground": {"$exists": False}},
            ],
        },
        {"$set": {f"{mddh_prefix}.source": "SLACK"}},
    )
    print(f"Updated {slack_prompts.modified_count} prompts with Slack source.")
    api_prompts = data_store["prompts"].update_many(
        {
            f"{mddh_prefix}.slack_info": {"$exists": False},
            "$or": [
                {f"{mddh_prefix}.playground": False},
                {f"{mddh_prefix}.playground": {"$exists": False}},
            ],
        },
        {"$set": {f"{mddh_prefix}.source": "API"}},
    )
    print(f"Updated {api_prompts.modified_count} prompts with API source.")

    playground_prompts = data_store["prompts"].update_many(
        {
            f"{mddh_prefix}.playground": True,
        },
        {"$set": {f"{mddh_prefix}.source": "PLAYGROUND"}},
    )
    print(
        f"Updated {playground_prompts.modified_count} prompts with Playground source."
    )
