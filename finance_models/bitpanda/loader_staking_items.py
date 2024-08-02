from finance_models.bitpanda.models import StakingItem, Transaction
import matplotlib.pyplot as plt
from os.path import join
from math import ceil


def load_staking_items(df, start_date, end_date):
    # create filter for rewards between a given timespan (If passed as an argument)
    _filter = (df['Transaction Type'] == 'reward')

    if start_date is not None:
        _filter = _filter & (df['Timestamp'] >= start_date)
    if end_date is not None:
        _filter = _filter & (df['Timestamp'] <= end_date)

    # get all assets
    assets = set(df[_filter]["Asset"].astype(str).values.tolist())

    for asset in assets:
        # Additionally filter for the Asset
        _transaction_filter = _filter & (df['Asset'] == asset)
        reward_data = df[_transaction_filter]
        rewards = []

        for index, reward in reward_data.iterrows():
            rewards.append(Transaction.create(reward))

        yield StakingItem(asset, rewards)  # load image paths


def create_staking_plot(entries_amount, dates, rewards, currency, cumulative, output_file, y_min=None, y_max=None):
    x_values = [date.strftime('%d %b %Y') for date in dates]

    bar_width = 0.75
    fig_width = max(bar_width * len(dates) * 2, 6)
    plt.figure(figsize=(fig_width, 6))
    # Use a darker green that complements the background
    figure = plt.bar(x_values, rewards, color='#4E8271', width=bar_width)

    # Add value annotations on top of each bar
    for bar in figure:
        yval = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,  # X position
            yval,  # Y position
            f'{yval:.2f} {currency}',  # Text to display
            ha='center',  # Horizontal alignment
            va='bottom',  # Vertical alignment
            fontsize=10,  # Font size
            color='#F7E7DC'  # Text color, same as label color for consistency
        )

    # Setting the labels and title colors to a lighter tone
    plt.xlabel('Date', color='#F7E7DC')
    plt.ylabel(f'Amount ({currency})', color='#F7E7DC')
    plt.title(f"Cumulative Rewards {entries_amount}" if cumulative else f"Rewards {entries_amount}", color='#F7E7DC')

    # Rotate x-axis labels and adjust size
    plt.xticks(rotation=45, ha='right', color='#F7E7DC')  # Rotate labels and set color
    plt.yticks(color='#F7E7DC')  # Set y-tick labels color
    plt.tight_layout()  # Automatically adjust subplot parameters to give some padding

    # Set grid color and style
    plt.grid(True, axis='y', color="#F7E7DC", linestyle='--', linewidth=1)

    # Set vertical range if specified
    if y_min is not None and y_max is not None:
        plt.ylim(y_min, y_max)

    ax = plt.gca()  # Get current axes
    ax.set_facecolor('#455A64')  # Background color of the plot area
    plt.gcf().set_facecolor('#455A64')  # Background color of the figure

    # Set the border (spines) color to a lighter tone
    for spine in ax.spines.values():
        spine.set_edgecolor('#F7E7DC')

    plt.savefig(output_file, bbox_inches='tight')

    # Clear the current figure
    plt.clf()
    plt.close()


def generate_staking_files(export_folder, dataframe, staking_items, start_date, end_date):

    for staking_item in staking_items:
        _filter = (dataframe['Transaction Type'] == 'reward') & (dataframe["Asset"] == staking_item.asset)

        if start_date is not None:
            _filter = _filter & (dataframe['Timestamp'] >= start_date)
        if end_date is not None:
            _filter = _filter & (dataframe['Timestamp'] <= end_date)

        filtered_df = dataframe[_filter].copy()
        # cumulative rewards
        filtered_df.loc[:, 'cumulative_rewards_fiat'] = filtered_df['Amount Fiat'].cumsum()

        paths = ([], [])

        cumulative_height = filtered_df['cumulative_rewards_fiat'].max()
        noncumalitive_height = filtered_df['Amount Fiat'].max()

        cumulative_height = cumulative_height + (cumulative_height / 10)
        noncumalitive_height = noncumalitive_height + (noncumalitive_height / 10)

        splitted_dataframes = []
        for i in range(0, ceil(len(filtered_df) / 10)):
            # index, df, from, to
            steps = 10

            splitted_df = filtered_df.iloc[i * steps: i * steps + 10]
            splitted_dataframes.append((i, splitted_df, i * steps + 1, i * steps + len(splitted_df)))

        for i, df, _from, to in splitted_dataframes:
            relative_cumulative_path = f'./StakingRewards{staking_item.asset}Cumulative_{i}.png'
            relative_noncumulative_path = f'./StakingRewards{staking_item.asset}NonCumulative{i}.png'
            cumulative_path = join(export_folder, relative_cumulative_path.replace("./", ""))
            noncumulative_path = join(export_folder, relative_noncumulative_path.replace("./", ""))

            fiat_currency = set(df["Fiat"].astype(str).values.tolist()).pop()
            create_staking_plot(f"({_from}-{to})", df['Timestamp'], df['Amount Fiat'], fiat_currency, False, noncumulative_path, 0, noncumalitive_height)
            create_staking_plot(f"({_from}-{to})", df['Timestamp'], df['cumulative_rewards_fiat'], fiat_currency, True, cumulative_path, 0, cumulative_height)

            paths[0].append(relative_noncumulative_path)
            paths[1].append(relative_cumulative_path)

        staking_item.image_paths.append(paths)
