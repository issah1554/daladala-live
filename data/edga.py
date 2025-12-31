import pandas as pd


def process_edges(input_file="edges.csv", output_file="processed_edges.csv"):
    # Read the input CSV file
    df = pd.read_csv(input_file)

    # 1. Remove duplicate edges (keeping first occurrence)
    df = df.drop_duplicates(subset=["from", "to"], keep="first")

    # Create a set of existing edges for fast lookup
    existing_edges = set(zip(df["from"], df["to"]))

    # Find edges that need their reverse added
    edges_to_add = []
    for _, row in df.iterrows():
        reverse_edge = (row["to"], row["from"])
        if reverse_edge not in existing_edges:
            edges_to_add.append(
                {"from": row["to"], "to": row["from"], "distance": row["distance"]}
            )
            # Add to existing edges to prevent duplicates in this run
            existing_edges.add(reverse_edge)

    # Create DataFrame for new edges and concatenate
    if edges_to_add:
        new_edges_df = pd.DataFrame(edges_to_add)
        df = pd.concat([df, new_edges_df], ignore_index=True)

    # 4. Sort to make forward and reverse edges consecutive
    # Create a temporary key for sorting
    df["sort_key"] = df.apply(
        lambda x: min(x["from"], x["to"]) + max(x["from"], x["to"]), axis=1
    )
    df = df.sort_values(by="sort_key").drop(columns="sort_key")

    # Reset index
    df = df.reset_index(drop=True)

    # Save the processed file
    df.to_csv(output_file, index=False)

    print(
        f"Processing complete. Original edges: {len(pd.read_csv(input_file))}, Processed edges: {len(df)}"
    )
    print(f"Results saved to {output_file}")


if __name__ == "__main__":
    process_edges()
