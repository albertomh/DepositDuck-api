/**
 * (c) 2024 Alberto Morón Hernández
 */

// `/welcome/` - onboarding flow
function onboardingState(tenancyEndDate) {
    return {
        name: "",
        depositAmount: null,
        tenancyStartDate: "",
        tenancyEndDate: tenancyEndDate || "",
        errors: {
            nameIsInvalid: false,
            depositAmountTooSmall: false,
            datesInWrongOrder: false,
            tenancyIsTooShort: false,
        },
        canSubmitForm: false,
        hasErrors() {
            // returns: bool
            Object.values(this.errors).some((value) => value === true);
        },
        allRequiredFieldsHaveValues() {
            // returns: bool
            const requiredFields = [
                this.name, this.depositAmount, this.tenancyStartDate, this.tenancyEndDate
            ];
            return !! requiredFields.some(field => field === '' || field === null);
        },
        validateName() {
            // returns: null
        },
        validateDepositAmount() {
            // returns: null
            this.errors.depositAmountTooSmall = this.depositAmount < 10;
        },
        daysBetweenDates(date1, date2) {
            // returns: number
            const diffInMs = date2 - date1;
            const msInDay = 1000 * 60 * 60 * 24;
            const diffInDays = Math.floor(diffInMs / msInDay);
            return diffInDays;
        },
        validateTenancyDates() {
            // returns: null
            if (!this.tenancyStartDate) {
                return;
            }

            const gap = this.daysBetweenDates(
                new Date(this.tenancyStartDate),
                new Date(this.tenancyEndDate)
            );
            this.errors.datesInWrongOrder = gap < 0;
            this.errors.tenancyIsTooShort = (0 < gap < 30);
        },
        validateForm() {
            // returns: null
            this.validateName()
            this.validateDepositAmount();
            this.validateTenancyDates();
            this.canSubmitForm = this.allRequiredFieldsHaveValues() && !this.hasErrors();
        }
    }
}
