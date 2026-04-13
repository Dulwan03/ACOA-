from modules.parallelism_module import run_parallelism_experiment
from modules.scheduling_module import run_scheduling_experiment
from modules.bus_module import run_bus_experiment
from modules.cache_module import run_cache_experiment
from modules.performance_module import plot_parallelism_results, print_results


def main():
    while True:
        print("\n=== Parallel Computing Demonstration Application ===")
        print("1. Run Module 1 - Parallelism")
        print("2. Run Module 2 - Scheduling")
        print("3. Run Module 3 - Bus")
        print("4. Run Module 4 - Cache")
        print("5. Plot Module 1 Graphs")
        print("6. Show Recorded Results")
        print("7. Run All Modules")
        print("0. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            run_parallelism_experiment()
        elif choice == "2":
            run_scheduling_experiment()
        elif choice == "3":
            run_bus_experiment()
        elif choice == "4":
            run_cache_experiment()
        elif choice == "5":
            plot_parallelism_results()
        elif choice == "6":
            print_results()
        elif choice == "7":
            run_parallelism_experiment()
            run_scheduling_experiment()
            run_bus_experiment()
            run_cache_experiment()
            plot_parallelism_results()
            print_results()
        elif choice == "0":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()