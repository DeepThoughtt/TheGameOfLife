#include <iostream>
#include <fstream>
#include <string>
#include <thread>
#include <chrono>

const int GAME_SIZE = 42;
const int GAME_MILLISECONDS = 1000;


void initialize_game_grid(int grid[GAME_SIZE][GAME_SIZE])
{
	int i = 0;
	
	while(i < GAME_SIZE)
	{
		grid[0][i] = -1;
		grid[i][0] = -1;
		grid[GAME_SIZE - 1][i] = -1;
		grid[i][GAME_SIZE - 1] = -1;
		i++;
	}
}


void reset_game_grid(int grid[GAME_SIZE][GAME_SIZE])
{	
	for(int i = 0; i < GAME_SIZE; i++)
		for(int j = 0; j < GAME_SIZE; j++)
			grid[i][j] = 0;
		
	initialize_game_grid(grid);
}


void print_game_grid(int grid[GAME_SIZE][GAME_SIZE])
{
	using std::cout;
	using std::endl;
	
	for(int i = 0; i < GAME_SIZE; i++)
	{
		for(int j = 0; j < GAME_SIZE; j++)
		{
			if(grid[i][j] == 0)
				cout << "  ";
			
			else if(grid[i][j] > 0)
				cout << "#" << " ";
			
			else
				cout << "X ";
		}
		cout << endl;
	}
}


void reset_data_grid(int grid[GAME_SIZE - 2][GAME_SIZE - 2])
{	
	for(int i = 0; i < GAME_SIZE - 2; i++)
		for(int j = 0; j < GAME_SIZE - 2; j++)
			grid[i][j] = 0;
}


void print_data_grid(int grid[GAME_SIZE - 2][GAME_SIZE - 2])
{
	using std::cout;
	using std::endl;
	
	for(int i = 0; i < GAME_SIZE - 2; i++)
	{
		for(int j = 0; j < GAME_SIZE - 2; j++)
			cout << grid[i][j] << " ";
		
		cout << endl;
	}
}


int data_sum(int grid[GAME_SIZE - 2][GAME_SIZE - 2])
{
	int sum = 0;
	
	for(int i = 0; i < GAME_SIZE - 2; i++)
		for(int j = 0; j < GAME_SIZE - 2; j++)
			sum += grid[i][j];
		
	return sum;
}


void update_data_grid_values(int data_grid[GAME_SIZE - 2][GAME_SIZE - 2], int game_grid[GAME_SIZE][GAME_SIZE])
{	
	for(int i = 1; i < GAME_SIZE - 1; i++)
	{
		for(int j = 1; j < GAME_SIZE - 1; j++)
		{
			int active_neighbors = 0;
				
			if(game_grid[i + 1][j] > 0)
				active_neighbors++;
			
			if(game_grid[i - 1][j] > 0)
				active_neighbors++;
				
			int x_index = i - 1;
			int y_index_1 = j - 1;
			int y_index_2 = j + 1;
				
			int loop_check = 0;
				
			while(loop_check < 3)
			{
				if(game_grid[x_index][y_index_1] > 0)
					active_neighbors++;	
					
				if(game_grid[x_index][y_index_2] > 0)
					active_neighbors++;
					
				x_index++;
				loop_check++;
			
				data_grid[i - 1][j - 1] = active_neighbors;
			}
		}
	}
}


void update_game_grid_values(int game_grid[GAME_SIZE][GAME_SIZE], int data_grid[GAME_SIZE - 2][GAME_SIZE - 2], int function = 2)
{
	// in the initialization we don't want to elaborate who lives and who dies
	if(function == 1)
	{
		for(int i = 1; i < GAME_SIZE - 1; i++)
			for(int j = 1; j < GAME_SIZE - 1; j++)
			{
				if(data_grid[i - 1][j - 1] == 1)
					game_grid[i][j] = 1;
			}
			
		return;
	}
	
	if(function == 2)
	{
		for(int i = 1; i < GAME_SIZE - 1; i++)
		{
			for(int j = 1; j < GAME_SIZE - 1; j++)
			{
				// OVERPOPULATION
				if(data_grid[i - 1][j - 1] > 3)
					game_grid[i][j] = 0;			
				
				// ISOLATION
				if(data_grid[i - 1][j - 1] < 2)
					game_grid[i][j] = 0;					
				
				if(data_grid[i - 1][j - 1] == 2 || data_grid[i - 1][j - 1] == 3)
				{
					// REPRODUCTION
					if(data_grid[i - 1][j - 1] == 3)
						game_grid[i][j] = data_grid[i - 1][j - 1];	
				}
			}
		}
	}
}


int load_data(std::string filename, int data_grid[GAME_SIZE - 2][GAME_SIZE - 2], int game_grid[GAME_SIZE][GAME_SIZE])
{
	std::ifstream input_stream;
	std::string final_filename("./configurations/");
	final_filename.append(filename);
	
	input_stream.open(final_filename.c_str());
	
	if(input_stream.fail())
	{
		input_stream.close();
		return 1;
	}
	
	for(int i = 0; i < GAME_SIZE - 2; i++)
		for(int j = 0; j < GAME_SIZE - 2; j++)
		{
			int initial = 0;
			input_stream >> initial;
			
			if(initial == 1)
				data_grid[i][j] = initial;
		}
		
	update_game_grid_values(game_grid, data_grid, 1);
	input_stream.close();
	return 0;
}


void update_log_file(int data_grid[GAME_SIZE - 2][GAME_SIZE - 2], int& iterations)
{
	std::ofstream output_stream;
	output_stream.open("./log/logfile.txt", std::ios_base::app);
	
	for(int i = 0; i < GAME_SIZE - 2; i++)
	{
		for(int j = 0; j < GAME_SIZE - 2; j++)
			output_stream << data_grid[i][j] << " ";
		
		output_stream << "\n";
	}
	
	output_stream << "\n--> END OF ITERATION " << iterations << "\n\n";
	output_stream.close();
	iterations++;
}


int main()
{
	using std::cout;
	using std::endl;
	using std::cin;
	
	int game_grid[GAME_SIZE][GAME_SIZE];
	int data_grid[GAME_SIZE - 2][GAME_SIZE - 2];
	
	reset_data_grid(data_grid);
	reset_game_grid(game_grid);
	
	cout << "<<THE GAME OF LIFE>>\n";
	cout << "--> RULES: \n";
	cout << "        1) Every alive cell with less than two adjacent alive cells, dies (isolation)\n";
	cout << "        2) Every alive cell with two or three adjacent alive cells survives to the next generation\n";
	cout << "        3) Every alive cell with more than three adjacent alive cells dies (overpopulation)\n";
	cout << "        4) Every dead cell with exactly three adjacent alive cells becomes alive (reproduction)\n";
	cout << endl;
	
	cout << "Insert first alive cells (index from 0 to " << GAME_SIZE - 3 << "): \n" << endl;
	
	print_game_grid(game_grid);
	
	char choice;
	cout << "Do you want to upload extern data (y/n)? ";
	cin >> choice;
	
	while(choice != 'y' && choice != 'n' || cin.fail())
	{
		cin.clear();
		cin.ignore();
		cout << "Data error, retry (y/n)? ";
		cin >> choice;
	}
	
	if(choice == 'y')
	{
		std::string filename;
		cin.ignore();
		cout << "Filename: ";
		std::getline(cin, filename);
		int status = 1;
		
		status = load_data(filename, data_grid, game_grid);
		while(status == 1)
		{
			cout << "Unable to find the file, do you want to retry (y/n)? ";
			cin >> choice;
			
			while(choice != 'y' && choice != 'n')
			{
				cin.clear();
				cin.ignore();
				cout << "Data error, retry (y/n)? ";
				cin >> choice;
			}
			
			if(choice == 'y')
			{
				cin.ignore();
				cout << "Filename: ";
				std::getline(cin, filename);
				status = load_data(filename, data_grid, game_grid);
			}
			
			if(choice == 'n')
			{
				cout << "Upload aborted\n";
				break;
			}
		}
		
		if(status == 0)
		{
			cout << "Upload successful\n";
			print_game_grid(game_grid);
		}
	}
	
	int input_x = 0;
	int input_y = 0;
	
	// starting configuration
	while(input_x >= 0 && input_y >= 0)
	{
		cout << "Insert data (between 0 and " << GAME_SIZE - 3 << "):\n>> Insert a number lower than 0 to stop inserting data \n";
		
		cout << "X: ";
		cin >> input_x;
		
		if(input_x < 0)
			break;
		
		cout << "Y: ";
		cin >> input_y;
		
		if(input_y < 0)
			break;
		
		if(input_x >= 0 && input_x < GAME_SIZE - 2 && input_y >= 0 && input_y < GAME_SIZE - 2)
		{
			data_grid[input_y][input_x] = 1;
			update_game_grid_values(game_grid, data_grid, 1);
			print_game_grid(game_grid);
		}
		
		else if(cin.fail() || input_x >= GAME_SIZE - 2 || input_y >= GAME_SIZE - 2)
		{
			cin.clear();
			cin.ignore();
			cout << "Data error, retry" << endl;
		}
	}
	
	char logfile_needed;
	cout << "Do you want to create a log file (y/n)? ";
	cin >> logfile_needed;
	
	while(logfile_needed != 'y' && logfile_needed != 'n' || cin.fail())
	{
		cin.clear();
		cin.ignore();
		cout << "Data error, retry (y/n): ";
		cin >> logfile_needed;
	}
	
	int iterations = 0;
	
	if(logfile_needed == 'y')
		update_log_file(data_grid, iterations);
	
	while(data_sum(data_grid) > 0)
	{
		std::this_thread::sleep_for(std::chrono::milliseconds(GAME_MILLISECONDS));
		
		update_data_grid_values(data_grid, game_grid);
		update_game_grid_values(game_grid, data_grid);
		print_game_grid(game_grid);
		
		if(logfile_needed == 'y')
			update_log_file(data_grid, iterations);
	}
	
	return 0;
}
